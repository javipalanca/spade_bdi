!start.

+!start <-
  ?receiver(X);
  .send(X, achieve, welcome(1));
  .wait(2000);
  .send(X, unachieve, welcome(N));
  .print("Unachieved").
