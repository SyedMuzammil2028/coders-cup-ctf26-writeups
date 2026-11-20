#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static void print_flag(void)
{
    char flag[128];
    FILE *file = fopen("flag.txt", "r");
    if (file == NULL || fgets(flag, sizeof(flag), file) == NULL) {
        fputs("The library cannot find its flag.\n", stderr);
        exit(1);
    }
    fclose(file);
    fputs(flag, stdout);
}

int main(void)
{
    struct {
        uint32_t shelves[8];
        uint32_t restricted_passcode;
    } library = { .shelves = {0}, .restricted_passcode = 0 };
    int shelf;
    uint32_t value;

    setvbuf(stdout, NULL, _IONBF, 0);
    puts("The Forbidden Shelf");
    puts("Enter a shelf number and a number to store there:");
    if (scanf("%d %u", &shelf, &value) != 2) {
        puts("The librarian needs two numbers.");
        return 1;
    }
    if (shelf < 0) {
        puts("Shelves cannot have negative numbers.");
        return 1;
    }

    /* The upper-bound check was accidentally omitted. */
    library.shelves[shelf] = value;

    if (library.restricted_passcode == 1337) {
        puts("The restricted section opens!");
        print_flag();
    } else {
        puts("The restricted section remains locked.");
    }
    return 0;
}
