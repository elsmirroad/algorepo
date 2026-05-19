#ifndef LC_HPP
#define LC_HPP

#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <algorithm>
#include <sstream>
#include <type_traits>

// LeetCode Data Structures
struct ListNode {
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode *next) : val(x), next(next) {}
};

struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
};

namespace lc {
    inline void print_status(bool passed, int id, const std::string& args, const std::string& res, const std::string& exp) {
        if (passed) {
            std::cout << "\033[92mPASSED\033[0m";
        } else {
            std::cout << "\033[91mFAILED\033[0m";
        }
        std::cout << " Test " << id << ": args " << args << " result " << res << " expected " << exp << std::endl;
    }

    // Helper to format basic types to string for output
    template<typename T>
    std::string to_str(const T& val) {
        if constexpr (std::is_same_v<T, std::string>) {
            return "\"" + val + "\"";
        } else if constexpr (std::is_same_v<T, bool>) {
            return val ? "true" : "false";
        } else {
            std::stringstream ss;
            ss << val;
            return ss.str();
        }
    }

    // Helper for vectors
    template<typename T>
    std::string to_str(const std::vector<T>& vec) {
        std::stringstream ss;
        ss << "[";
        for (size_t i = 0; i < vec.size(); ++i) {
            ss << to_str(vec[i]) << (i == vec.size() - 1 ? "" : ",");
        }
        ss << "]";
        return ss.str();
    }
}

#endif
