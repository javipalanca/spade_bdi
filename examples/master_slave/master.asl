!start.

+!start
 <-
  -start;
  !obj2.

+!obj2: type(inc)
 <-
  ?slave1(X);
  ?slave2(Y);
  .send(X, tell, increase(2));
  .send(Y, tell, increase(5));
  .wait(300);
  !obj2.

+!obj2: type(dec)
 <-
  ?slave1(X);
  ?slave2(Y);
  .send(X, tell, decrease(2));
  .send(Y, tell, decrease(5));
  .wait(300);
  !obj2.

+!obj2: not type(_)
 <-
  ?slave1(X);
  ?slave2(Y);
  .print("Finishing");
  .send(X, untell, increase(2));
  .send(Y, untell, increase(5));
  .send(X, untell, decrease(2));
  .send(Y, untell, decrease(5)).
