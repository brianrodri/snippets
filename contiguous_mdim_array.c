#include <stdio.h>
#include <stdlib.h>

/* Returns a pointer to a contiguous m-dimensional array w/ the given
dimensions. Does not protect against overflow, so be wary of large values of m
and dimension sizes. Consider using floating m-dimensional arrays for such cases
instead. Because it is completely contiguous, you free the entire array by
freeing the returned base pointer. Implementation further below. */
void * malloc_mdim_arr(size_t * dim_sizes, size_t m, size_t elm_size, size_t elm_align);



int
main(int argc, char ** argv)
{
	size_t dims[3] = { 3, 4, 8 };
	double *** arr = malloc_mdim_arr(dims, 3, sizeof(double), __alignof__(double));

	for (int i = 0; i < 3; ++i) {
		for (int j = 0; j < 4; ++j) {
			for (int k = 0; k < 8; ++k) {
				arr[i][j][k] = i*j*0.5 - j*k*7.75 + k*i*3.25;
				printf("arr[%d][%d][%d] = %f\n", i, j, k, arr[i][j][k]);
			}
		}
	}

	free(arr);
	return 0;
}

void *
malloc_mdim_arr(size_t * dim_sizes, size_t m, size_t elm_size, size_t elm_align)
{
	if (dim_sizes == NULL || m == 0 || elm_size == 0 || elm_align == 0) {
		return NULL;
	}

	size_t ptr_space, pad_space, elm_space, * prod_arr;
	void ** arr;

	if ((prod_arr = malloc((m - 1) * sizeof(size_t))) == NULL) {
		return NULL;
	}

	ptr_space = 0;

	for (size_t i = 0; i < (m - 1); ++i) {
		prod_arr[i] = (i) ? (prod_arr[i - 1] * dim_sizes[i]) : dim_sizes[i];
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

	void ** ptr_at, * ptr_to;
	ptr_at = arr;
	ptr_to = (void *) arr + prod_arr[0] * sizeof(void *);

	for (size_t cur_dim = 1; cur_dim < m; ++cur_dim) {
		size_t increments;

		if (cur_dim == (m - 1)) {
			ptr_to += pad_space;
			increments = elm_size * dim_sizes[cur_dim];

		} else {
			increments = sizeof(void *) * dim_sizes[cur_dim];
		}

		while (prod_arr[cur_dim - 1]--) {
			*++ptr_at = ptr_to;
			ptr_to += increments;
		}
	}

	free(prod_arr);
	return (void *) arr;
}
