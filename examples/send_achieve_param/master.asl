!start.

+!start <-
 	 ?slave1(X);
    .print("Sending message to slave1");
    .send(X, achieve, say("Hello BDI"));
    .print("Message sent").
