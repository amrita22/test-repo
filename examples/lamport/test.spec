vars
    s1 s2 s3

rules
    s1 >= 1 ->
        s1' = s1+0,
        s2' = s2+1;

    s1 >= 1,
    s2 >= 1 ->
        s1' = s1-1,
        s2' = s2-1,
        s3' = s3+1;

    s3 >=1 ->
        s3' = s3-1,
        s1' = s1+1;

init
    s1=2, s2=0, s3=0

target
    s1=0, s2=0, s3=2