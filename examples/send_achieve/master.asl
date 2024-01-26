!start.

+!start <-
 	 ?slave1(X);
    .print("Sending message");
    .send(X, achieve, hello);
    .print("Message sent");
    .send(X, achieve, bye).
