#include <stdio.h>
#include <stdlib.h>

/*
Returns a pointer to a jagged, contiguous, m-dimensional array w/ given sizes.
Does not protect against overflow, so be wary of large values of m and dimension
sizes. Consider using floating m-dimensional arrays for such cases instead.
Because it is completely contiguous, you free the entire array by freeing the
returned base pointer. Implementation further below.

WARNING: For an [M][N]...[Z] array 'arr', the elements do NOT live in the range:
	[ 'arr' , 'arr + M*N*...*Z' )
So you must use the & operator to find the range like so:
	[ '&arr[0][0]...[0]' , '&arr[M-1][N-1]...[Z-1] +1' )
*/
void * malloc_mdim_arr(size_t * dim_sizes, size_t m, size_t elm_size, size_t elm_align);



int
main()
{
	int i, j, k;
	size_t dims[3] = { 3, 8, 4 };
	double *** arr = malloc_mdim_arr(dims, 3, sizeof(double), __alignof__(double));
	printf("%p\n", (void *) arr);

	for (i = 0; i < 3; ++i) {
		for (j = 0; j < 8; ++j) {
			for (k = 0; k < 4; ++k) {
				arr[i][j][k] = i*j*0.5 - j*k*7.75 + k*i*3.25;
				printf("arr[%d][%d][%d]/%p = %f\n", i, j, k, (void *) &arr[i][j][k], arr[i][j][k]);
			}
		}
	}

	free(arr);
	return 0;
}

void *
malloc_mdim_arr(size_t * dim_sizes, size_t m, size_t elm_size, size_t elm_align)
{
	size_t ptr_space, pad_space, elm_space, * prod_arr, increments, i;
	void ** arr, ** ptr_at, * ptr_to;

	if (dim_sizes == NULL || m == 0 || elm_size == 0 || elm_align == 0) {
		return NULL;
	}

	if (m == 1) {
		return malloc(dim_sizes[0] * elm_size);
	}

	if ((prod_arr = malloc((m - 1) * sizeof(size_t))) == NULL) {
		return NULL;
	}

	ptr_space = prod_arr[0] = dim_sizes[0];

	for (i = 1; i < (m - 1); ++i) {
		prod_arr[i] = prod_arr[i - 1] * dim_sizes[i];
		ptr_space += prod_arr[i];
	}

	ptr_space *= sizeof(void *);
	elm_space = prod_arr[m - 2] * dim_sizes[m - 1] * elm_size;
	pad_space = elm_align - (ptr_space % elm_align);
	pad_space = (pad_space == elm_align) ? 0 : pad_space;

	if ((arr = malloc(ptr_space + pad_space + elm_space)) == NULL) {
		free(prod_arr);
		return NULL;
	}

	ptr_at = arr;
	ptr_to = (void *) arr + dim_sizes[0] * sizeof(void *);

	for (i = 1; i < m; ++i) {
		if (i == (m - 1)) {
			ptr_to += pad_space;
			increments = dim_sizes[i] * elm_size;

		} else {
			increments = dim_sizes[i] * sizeof(void *);
		}

		while (prod_arr[i - 1]--) {
			*ptr_at++ = ptr_to;
			ptr_to += increments;
		}
	}

	free(prod_arr);
	return (void *) arr;
}
