+!welcome(N) <-
  while (true) {
    .wait(500);
    .print("Welcome", N);
  }.

+!welcome(N, M) <-
  while (true) {
    .wait(500);
    .print("Welcome", N, "-", M);
  }.
