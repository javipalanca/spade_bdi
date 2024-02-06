!start.

+!start
   <-
      ?receiver(X);
      .print("Ask for Plan");
      .send(X, askHow, "+!hello(N)");
      .print("Plan added...");
      .wait(1000);
      !hello(X)
   .
