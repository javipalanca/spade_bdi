// Coordinator ASL: Orchestrates Tuner -> Validator -> Save with one retry

// When receiving task parameters, start coordination with attempt 0
+task_params(D, M) <-
    .print("Task params");
    !coordinate(D, M, 0).

// If there's no prediction yet, request adjustment (tuning)
+!coordinate(D, M, Attempt) : not predicted(_, _, _, _) <-
    .print("BDI: requesting prediction from Tuner...");
    py.tune(D, M).

// When we have prediction, request validation
+predicted(V, H, TE, TC) : task_params(D, M) <-
    .print("BDI: validating prediction...");
    py.validate(V, H, TE, TC).

// If validation is OK: save and finish
+validation_ok : task_params(D, M) & predicted(V, H, TE, TC) <-
    .print("BDI: saving valid parameters...");
    py.save(D, M, V, H, TE, TC);
    -predicted(V, H, TE, TC).

// If validation fails and it's the first attempt: retry with +10 in hardness
+validation_failed(Reason) : task_params(D, M) & predicted(V, H, TE, TC) & attempt(0) <-
    .print("BDI: validation failed (first attempt). Retrying with +10 hardness...");
    py.tune_adjust(D, M, 10);
    -predicted(V, H, TE, TC);
    -validation_failed(Reason);
    -attempt(0);
    +attempt(1).

// If it fails again after retry: report failure and finish
+validation_failed(Reason) : attempt(1) <-
    .print("BDI: validation failed after retry: ");
    .print(Reason).
