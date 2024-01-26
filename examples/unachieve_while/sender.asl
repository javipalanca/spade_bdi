!start.

+!start <-
  ?receiver(X);
  .print("start achievement ...");
  .send(X, achieve, welcome(2));
  .print("start achievement ...");
  .send(X, achieve, welcome(3));
  .wait(100);
  .print("start achievement ...");
  .send(X, achieve, welcome(3, 2));
  .wait(2000);
  .print("cancel achievent ...");
  .send(X, unachieve, welcome(N, M));
  .print("cancelled.").
