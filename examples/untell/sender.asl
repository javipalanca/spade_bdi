!start.

+!start : true
   <-
      ?receiver(X);
      .send(X,tell, name("John"));
      .send(X, achieve, check);
      .send(X, untell, name("Andrew"));
      .print("Disproving a belief that does not exist...");
      .send(X, achieve, check);
      .send(X, untell, name("John"));
      .print("Disproving a belief that does exist...");
      .send(X, achieve, check).
