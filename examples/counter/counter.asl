counter(8).
type(dec).
!init.

+!init
 <-
  .print("Starting....");
  !obj2.


 +!obj2: type(inc)
 <-
  .print("Increasing");
  ?counter(X);
  -+counter(X+1);
  .wait(100);
    !obj2.


+!obj2: type(dec)
 <-
  .print("Decreasing");
  ?counter(X);
  -+counter(X-1);
  .wait(100);
    !obj2.


+!obj2: not type(_)
 <-
  .print("Waiting");
  .wait(100);
    !obj2.
