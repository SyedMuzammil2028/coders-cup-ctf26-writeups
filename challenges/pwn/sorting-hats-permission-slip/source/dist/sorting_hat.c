#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

static void print_flag(void)
{
    char flag[128];
    FILE *file = fopen("flag.txt", "r");
    if (file == NULL || fgets(flag, sizeof(flag), file) == NULL) {
        fputs("The Sorting Hat cannot find its flag.\n", stderr);
        exit(1);
    }
    fclose(file);
    fputs(flag, stdout);
}

int main(void)
{
    /* Keep the two fields adjacent and in the stated order. */
    struct {
        char student_name[32];
        uint32_t admitted;
    } application = { .student_name = {0}, .admitted = 0 };

    setvbuf(stdout, NULL, _IONBF, 0);
    puts("The Sorting Hat's Permission Slip");
    puts("Give the hat your name:");

    /* Intentionally read across student_name into the next stack field. */
    if (read(STDIN_FILENO, application.student_name, sizeof(application)) <= 0) {
        return 1;
    }

    if (application.admitted != 0) {
        puts("The hat approves your entry!");
        print_flag();
    } else {
        puts("The hat says your application is still pending.");
    }
    return 0;
}
