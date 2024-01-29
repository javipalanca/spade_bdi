!start.

+!start : true
   <-
      ?receiver(X);
      .print("Telling plan to receiver");
      .wait(2000);
      .send(X, tellHow, "+!hello(N) : not meet(\"John\") & meet(\"Paul\") <- .print(\"I am a plan called \", N).");
      .wait(500);
      .send(X, achieve, hello("Ringo"));
      .send(X, achieve, hello("Paul")).
