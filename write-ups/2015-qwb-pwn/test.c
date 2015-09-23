#include<stdio.h>
int main()
{
	char *a, *b, *c, *d;
	a = malloc(128);
	b = malloc(128);
	c = malloc(128);
	d = malloc(128);

	printf("%x\n", a);
	free(c);
	free(d);
	free(b);
	free(a);

	printf("%x\n", b);
	printf("%x\n", c);
	printf("%x\n", d);
	return 0;
}