#ifndef LC_H
#define LC_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef bool boolean;

// LeetCode Data Structures
struct ListNode {
    int val;
    struct ListNode *next;
};

struct TreeNode {
    int val;
    struct TreeNode *left;
    struct TreeNode *right;
};

// Colors for terminal output
#define CLR_RED  "\033[91m"
#define CLR_GRN  "\033[92m"
#define CLR_RST  "\033[0m"

static void print_status(bool passed, int id, const char* args, const char* res, const char* exp) {
    if (passed) {
        printf("%sPASSED%s", CLR_GRN, CLR_RST);
    } else {
        printf("%sFAILED%s", CLR_RED, CLR_RST);
    }
    printf(" Test %d: args %s result %s expected %s\n", id, args, res, exp);
}

#endif
