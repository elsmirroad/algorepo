package main

import (
	"fmt"
	"reflect"
	"encoding/json"
)

// LeetCode Data Structures
type ListNode struct {
	Val  int
	Next *ListNode
}

type TreeNode struct {
	Val   int
	Left  *TreeNode
	Right *TreeNode
}

// Helpers
func SerializeList(head *ListNode) []int {
	res := []int{}
	for head != nil {
		res = append(res, head.Val)
		head = head.Next
	}
	return res
}

func PrintStatus(passed bool, id int, args string, res string, exp string) {
	status := "\033[91mFAILED\033[0m"
	if passed {
		status = "\033[92mPASSED\033[0m"
	}
	fmt.Printf("%s Test %d: args %s result %s expected %s\n", status, id, args, res, exp)
}

func Equal(a, b interface{}) bool {
	return reflect.DeepEqual(a, b)
}
