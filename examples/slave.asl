counter(0).

+increase(Inc)[source(S)]: master(M) & .substring(M,S,R)
 <- 
  .print("increasing");
  ?counter(X);
  .print(X);
  -+counter(X+Inc).

+decrease(Dec)[source(S)]: master(M) & .substring(M,S,R)
 <- 
  .print("decreasing");
  ?counter(X);
  .print(X);
  -+counter(X-Dec).

-increase(Inc)[source(S)]: master(M) & .substring(M,S,R)
 <-
  .print("DELETING increase BELIEF from an untell message").

-decrease(Dec)[source(S)]: master(M) & .substring(M,S,R)
 <-
  .print("DELETING decrease BELIEF from an untell message").
