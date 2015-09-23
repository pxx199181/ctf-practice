#include <stdio.h>
int main()
{
	char *a, *b, *c, *d, *e, *f;
	a = malloc(0xd0);
	b = malloc(0xd0);
	c = malloc(0xd0);

	printf("a:%08p\n", a);
	printf("b:%08p\n", b);
	printf("c:%08p\n", c);

	free(a);
	free(b);
	free(c);

	a = malloc(0xd8);
	printf("a:%08p\n", a);

	b = malloc(0x9);
	printf("b:%08p\n", b);
	b = realloc(b, 0xd8);
	printf("b:%08p\n", b);

	c = malloc(0xd8);
	printf("c:%08p\n", c);


	d = malloc(0xd0);
	e = malloc(0xd0);
	f = malloc(0xd0);

	printf("d:%08p\n", d);
	printf("e:%08p\n", e);
	printf("f:%08p\n", f);

	free(d);
	free(e);
	free(f);

	d = malloc(0xd8);
	printf("d:%08p\n", d);

	e = malloc(0x9);
	printf("e:%08p\n", e);
	e = realloc(e, 0xd8);
	printf("e:%08p\n", e);

	f = malloc(0xd8);
	printf("f:%08p\n", f);

	return 0;
}