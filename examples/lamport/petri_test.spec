vars
    p0 p1 p2 pt pf

rules
    p0 >= 2 ->
	       p0' = p0-1,
	       pf' = pf+1;

	p1 >= 2 ->
	       p1' = p1-2,
	       p2' = p2+1,
	       pf' = pf+1;

	p2 >= 2 ->
	       p2' = p2-2,
	       p1' = p1+1,
	       pt' = pt+1;

	p0 >= 1,
    p1 >= 1 ->
	       p1' = p1+0,
	       p0' = p0-1,
	       pt' = pt+1;

	p0 >= 1,
    p2 >= 1 ->
	       p2' = p2+0,
	       p0' = p0-1,
	       pf' = pf+1;

	p2 >= 1,
    p1 >= 1 ->
	       p1' = p1-1,
	       p2' = p2-1,
	       p0' = p0+1,
	       pf' = pf+1;

    p0 >= 1,
    pt >= 1 ->
	       p0' = p0+0,
	       pt' = pt-1,
	       pf' = pf+1;

	p1 >= 1,
    pf >= 1 ->
	       p1' = p1+0,
	       pf' = pf-1,
	       pt' = pt+1;

	p2 >= 1,
    pt >= 1 ->
	       p2' = p2+0,
	       pt' = pt-1,
	       pf' = pf+1;

init
    p0=3, p1=2, p2=3, pt=0, pf=0

target
    pt>=5