#include "stdio.h"
int main(){
	int i;
	for (i = 0; i < 10; i++){
		printf("%d--%d\n", i, i*i);
	}
	return 0;
}