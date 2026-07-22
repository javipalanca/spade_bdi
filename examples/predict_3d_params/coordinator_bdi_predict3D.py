"""
SPADE-BDI Coordinator that orchestrates Tuner -> Validator -> Save

- TunerAgent (SPADE base): receives JSON {hardness, material} and responds [speed, layer_height, extruder_temp, bed_temp].
- ValidatorAgent (SPADE base): validates the 4 parameters and responds {ok, reasons?, expected?}.
- CoordinatorBDIAgent (SPADE-BDI): plans in ASL (coordinator.asl) + Python actions:
  py.tune, py.tune_adjust, py.validate, py.save. 
  Translates responses to beliefs (predicted, validation_ok/failed).

Execution:
- Starts the 3 agents, sets belief task_params(HardnessStr, Material) and executes the plans.
"""

# Standard libraries
import asyncio
import json
import logging
import os
import random
from datetime import datetime
from typing import Optional

# Third-party libraries
import agentspeak as asp
import joblib
import pandas as pd
import spade
from spade import wait_until_finished
from colorama import Fore, Style, init
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
from spade_bdi.bdi import BDIAgent

# Initialize colorama for Windows compatibility
init(autoreset=True)

# Agent color scheme
AGENT_COLORS = {
    "COORDINATOR": Fore.MAGENTA,
    "TUNER": Fore.BLUE,
    "VALIDATOR": Fore.LIGHTYELLOW_EX,  
    "SYSTEM": Fore.WHITE
}

def print_banner(title: str, color: str = Fore.CYAN):
    """Print an attractive banner for section headers."""
    width = 60
    border = "═" * width
    print(f"\n{color}╔{border}╗")
    print(f"║{title.center(width)}║")
    print(f"╚{border}╝{Style.RESET_ALL}")

def print_agent_msg(agent_name: str, message: str, color: str = None, status: str = "INFO"):
    """Print formatted agent messages."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    status_colors = {
        "INFO": Fore.CYAN,
        "SUCCESS": Fore.GREEN,
        "ERROR": Fore.RED,
        "WARNING": Fore.YELLOW,
        "PROCESSING": Fore.LIGHTRED_EX
    }
    status_color = status_colors.get(status, Fore.WHITE)
    # Use agent-specific color if not provided
    agent_color = color or AGENT_COLORS.get(agent_name, Fore.WHITE)
    print(f"{Fore.WHITE}[{timestamp}] {status_color}[{status}] {agent_color}{agent_name}: {message}{Style.RESET_ALL}")

def print_data(label: str, data, color: str = Fore.YELLOW):
    """Print formatted data with label."""
    print(f"{color}📊 {label}: {data}{Style.RESET_ALL}")


"""SPADE agent behaviours."""
"""Receiver for Coordinator BDI agent: receives responses from Tuner/Validator and maps them to BDI beliefs."""
class Receiver(CyclicBehaviour):
    async def run(self):
        # Receives responses from Tuner/Validator and maps them to BDI beliefs
        msg = await self.receive(timeout=1)
        if not msg:
            return
        try:
            data = json.loads(msg.body)
        except Exception:
            return
        # Tuner: list of 4 values -> predicted(V,H,TE,TC)
        if isinstance(data, list) and len(data) == 4:
            v, h, te, tc = data
            self.agent.bdi.set_belief("predicted", v, h, te, tc)
        # Validator: dict with ok
        elif isinstance(data, dict) and "ok" in data:
            if data.get("ok"):
                self.agent.bdi.set_belief("validation_ok")
            else:
                reasons = ", ".join(data.get("reasons", [])[:3]) if data.get("reasons") else data.get("error", "unknown")
                self.agent.bdi.set_belief("validation_failed", reasons)

"""3D parameter validator."""
class ValidateBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=30)
        if not msg:
            return
        try:
            data = json.loads(msg.body) if msg.body else {}
            if isinstance(data, list) and len(data) == 4:
                speed, layer_height, extruder_temperature, bed_temperature = data
            else:
                speed = data.get("speed")
                layer_height = data.get("layer_height")
                extruder_temperature = data.get("extruder_temperature")
                bed_temperature = data.get("bed_temperature")
            errors = []
            if not (30 <= float(speed) <= 120): errors.append("speed out of range [30,120] mm/s")
            if not (0.10 <= float(layer_height) <= 0.30): errors.append("layer_height out of range [0.10,0.30] mm")
            if not (180 <= float(extruder_temperature) <= 240): errors.append("extruder_temperature out of range [180,240] °C")
            if not (50 <= float(bed_temperature) <= 70): errors.append("bed_temperature out of range [50,70] °C")
            result = {"ok": len(errors) == 0}
            if errors:
                result["reasons"] = errors
                result["expected"] = {
                    "speed": "[30,120] mm/s",
                    "layer_height": "[0.10,0.30] mm",
                    "extruder_temperature": "[180,240] °C",
                    "bed_temperature": "[50,70] °C",
                }
                print_agent_msg("VALIDATOR", f"❌ Validation failed with {len(errors)} errors:", status="ERROR")
                for i, error in enumerate(errors, 1):
                    print(f"    {AGENT_COLORS['VALIDATOR']}• {error}{Style.RESET_ALL}")
            else:
                print_agent_msg("VALIDATOR", "✅ All parameters are valid!", status="SUCCESS")
            reply = msg.make_reply()
            reply.body = json.dumps(result, ensure_ascii=False)
            await self.send(reply)
        except Exception as e:
            reply = msg.make_reply()
            reply.body = json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)
            await self.send(reply)

"""3D parameter predictor using ML model."""
class PredictTuningBehaviour(CyclicBehaviour):
    def predict(self, hardness: float, material: str):
        bundle=joblib.load("./regresion3d_simple.joblib")
        model = bundle["model"]
        cols = bundle["feature_columns"]
        hardness_col = bundle["hardness_col"]
        mat_prefix = bundle["material_prefix"]
        targets = bundle["targets"]
        X = pd.DataFrame([[0] * len(cols)], columns=cols)
        X.loc[0, hardness_col] = hardness
        mat_col = f"{mat_prefix}{material}"
        if mat_col in X.columns:
            X.loc[0, mat_col] = 1
        y_pred = model.predict(X)[0]
        return {targets[i]: float(y_pred[i]) for i in range(len(targets))}
    async def run(self):
        print_agent_msg("TUNER", "🔍 Waiting for prediction request...", status="PROCESSING")
        msg = await self.receive(timeout=30)
        if not msg:
            print_agent_msg("TUNER", "⏰ No message received within expected time", status="WARNING")
            return
        try:
            data = json.loads(msg.body) if msg.body else {}
            _hardness = data.get("hardness")
            _material = data.get("material")
        except Exception:
            _hardness = None
            _material = None
        
        print_agent_msg("TUNER", f"🎯 Processing: Hardness={_hardness}, Material={_material}", status="PROCESSING")
        predicted_value = self.predict(_hardness, _material)
        
        speed = int(predicted_value["print_speed"]) 
        layer_height = round(predicted_value["layer_height"], 2)
        bed_temperature = int(predicted_value["bed_temperature"]) 
        extruder_temperature = int(predicted_value["nozzle_temperature"]) 
        values = [speed, layer_height, extruder_temperature, bed_temperature]
        
        print_agent_msg("TUNER", "🔮 Prediction completed successfully!", status="SUCCESS")
        print_data("Predicted Parameters", {
            "Speed": f"{speed} mm/s",
            "Layer Height": f"{layer_height} mm", 
            "Extruder Temp": f"{extruder_temperature}°C",
            "Bed Temp": f"{bed_temperature}°C"
        }, AGENT_COLORS['TUNER'])
        reply = msg.make_reply()
        reply.body = json.dumps(values, ensure_ascii=False)
        await self.send(reply)

"""SPADE-BDI Coordinator Agent."""
class CoordinatorAgentBDI(BDIAgent):
    async def setup(self):
        print_agent_msg("COORDINATOR", "🚀 BDI Agent initialized successfully", status="SUCCESS")
        pass

    def add_custom_actions(self, actions):
        """Registers Python actions callable from ASL."""
        # Map hardness from text to base numeric value
        hardness_map = {"low": 50, "medium": 65, "high": 80}
        @actions.add("py.tune", 2)
        def _tune(agent, term, intention):
            print_agent_msg("COORDINATOR", "🎯 Executing py.tune action", status="PROCESSING")
            D = asp.grounded(term.args[0], intention.scope)
            M = asp.grounded(term.args[1], intention.scope)
            hardness_num = hardness_map.get(str(D).lower(), 60)
            payload = {"hardness": hardness_num, "material": str(M)}
            print_data("Tuning Request", f"Hardness: {hardness_num}, Material: {M}", AGENT_COLORS['COORDINATOR'])
            msg = Message(to="tuner1@localhost", body=json.dumps(payload), metadata={})
            # Send asynchronously using BDI behaviour to have access to send()
            self.submit(self.bdi.send(msg))
            yield
        @actions.add("py.tune_adjust", 3)
        def _tune_adjust(agent, term, intention):
            print_agent_msg("COORDINATOR", "🔧 Executing py.tune_adjust action", status="PROCESSING")
            D = asp.grounded(term.args[0], intention.scope)
            M = asp.grounded(term.args[1], intention.scope)
            delta = asp.grounded(term.args[2], intention.scope)
            hardness_num = hardness_map.get(str(D).lower(), 60) + int(delta)
            payload = {"hardness": hardness_num, "material": str(M)}
            print_data("Adjusted Tuning", f"Hardness: {hardness_num} (+{delta}), Material: {M}", AGENT_COLORS['COORDINATOR'])
            msg = Message(to="tuner1@localhost", body=json.dumps(payload), metadata={})
            self.submit(self.bdi.send(msg))
            yield
        @actions.add("py.validate", 4)
        def _validate(agent, term, intention):
            print_agent_msg("COORDINATOR", "✅ Executing py.validate action", status="PROCESSING")
            V = float(asp.grounded(term.args[0], intention.scope))
            H = float(asp.grounded(term.args[1], intention.scope))
            TE = float(asp.grounded(term.args[2], intention.scope))
            TC = float(asp.grounded(term.args[3], intention.scope))
            payload = [V, H, TE, TC]
            print_data("Validation Request", f"Speed: {V}, Height: {H}, ExtruderT: {TE}, BedT: {TC}", AGENT_COLORS['COORDINATOR'])
            msg = Message(to="validator1@localhost", body=json.dumps(payload), metadata={})
            self.submit(self.bdi.send(msg))
            yield
        @actions.add("py.save", 6)
        def _save(agent, term, intention):
            print_agent_msg("COORDINATOR", "💾 Executing py.save action", status="PROCESSING")
            D = asp.grounded(term.args[0], intention.scope)
            M = asp.grounded(term.args[1], intention.scope)
            V = float(asp.grounded(term.args[2], intention.scope))
            H = float(asp.grounded(term.args[3], intention.scope))
            TE = float(asp.grounded(term.args[4], intention.scope))
            TC = float(asp.grounded(term.args[5], intention.scope))
            path = os.path.join(os.path.dirname(__file__), f"tuning_result_bdi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            data = {
                "hardness": str(D),
                "material": str(M),
                "speed": V,
                "layer_height": H,
                "extruder_temperature": TE,
                "bed_temperature": TC,
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print_agent_msg("COORDINATOR", f"💾 Parameters saved successfully!", status="SUCCESS")
            print_data("Save Location", path, AGENT_COLORS['COORDINATOR'])
            # Signal end to the app
            self.save_completed = True
            self.last_save_path = path
            yield

"""SPADE Validator Agent."""
class ValidatorAgent(Agent):
    async def setup(self):
        print_agent_msg("VALIDATOR", "🛡️ Validator Agent started", status="SUCCESS")
        pass

"""SPADE Tuner Agent."""
class TunerAgent(Agent):
    async def setup(self):
        print_agent_msg("TUNER", "🔧 Tuner Agent started", status="SUCCESS")
        pass

async def main():
    print_banner("🤖 SPADE-BDI 3D PRINTING COORDINATOR 🤖", Fore.CYAN)
    print_agent_msg("SYSTEM", "Initializing multi-agent system...", status="INFO")
    
    """ Create agents """
    coordinator = CoordinatorAgentBDI(jid='coordinator1@localhost', password='pass', asl="coordinator.asl")
    validator = ValidatorAgent(jid='validator1@localhost', password='pass')
    tuner = TunerAgent(jid='tuner1@localhost', password='pass')
    
    """ Setup behaviours """
    coordinator_receiver = Receiver()
    coordinator.add_behaviour(coordinator_receiver)
    coordinator.receiver = coordinator_receiver
    
    validator_validatebehaviour = ValidateBehaviour()
    validator.add_behaviour(validator_validatebehaviour)
    validator.validate_behaviour = validator_validatebehaviour
    
    tuner_predicttuningbehaviour = PredictTuningBehaviour()
    tuner.add_behaviour(tuner_predicttuningbehaviour)
    tuner.predict_tuning_behaviour = tuner_predicttuningbehaviour
    
    print_banner("🚀 AGENT STARTUP SEQUENCE 🚀", Fore.GREEN)

    print_agent_msg("VALIDATOR", "Starting validation agent...", status="INFO")
    await validator.start(auto_register=True)
    print_agent_msg("VALIDATOR", "✅ Agent started successfully", status="SUCCESS")
    
    print_agent_msg("TUNER", "Starting prediction agent...", status="INFO")
    await tuner.start(auto_register=True)
    print_agent_msg("TUNER", "✅ Agent started successfully", status="SUCCESS")
    
    print_agent_msg("COORDINATOR", "Starting BDI coordinator...", status="INFO")
    coordinator.bdi.set_belief('task_params','60','PLA')
    await coordinator.start(auto_register=True)
    print_agent_msg("COORDINATOR", "✅ Agent started successfully", status="SUCCESS")
    
    print_banner("⏰ EXECUTION WITH 30s TIMEOUT ⏰", Fore.YELLOW)
    
    # Create a timeout task that will stop agents after 30 seconds
    async def timeout_task():
        await asyncio.sleep(15)
        print_banner("⏰ TIMEOUT REACHED ⏰", Fore.YELLOW)
        print_agent_msg("SYSTEM", "Stopping all agents after 15 seconds...", status="WARNING")
        await coordinator.stop()
        await validator.stop()
        await tuner.stop()
        print_agent_msg("SYSTEM", "🔴 All agents stopped due to timeout", status="INFO")
    
    # Run agents with timeout
    timeout_future = asyncio.create_task(timeout_task())
    agents_future = asyncio.create_task(wait_until_finished([coordinator, validator, tuner]))
    
    try:
        # Wait for either the agents to finish naturally or timeout
        done, pending = await asyncio.wait(
            [timeout_future, agents_future],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel any remaining tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
                
    except KeyboardInterrupt:
        print_banner("🛑 MANUAL STOP 🛑", Fore.RED)
        print_agent_msg("SYSTEM", "Keyboard interrupt received. Stopping agents...", status="WARNING")
        await coordinator.stop()
        await validator.stop()
        await tuner.stop()
        timeout_future.cancel()
        agents_future.cancel()
        print_agent_msg("SYSTEM", "🔴 All agents stopped manually", status="INFO")
    
    print_banner("🏁 EXECUTION COMPLETED 🏁", Fore.MAGENTA)

if __name__ == "__main__":
    spade.run(main())
