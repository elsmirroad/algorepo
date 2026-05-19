function runTest(solution, testCases) {
    if (!solution || !testCases) return;

    testCases.forEach((tc, index) => {
        try {
            const { inputs, expected } = tc;
            const parsedInputs = inputs.map(i => {
                try { return JSON.parse(i.replace(/'/g, '"')); }
                catch (e) { return i; }
            });

            let parsedExpected;
            try {
                parsedExpected = JSON.parse(expected.replace(/'/g, '"'));
            } catch (e) {
                parsedExpected = expected;
            }

            let result;
            if (typeof solution === 'function') {
                result = solution(...parsedInputs);
            } else if (solution && solution.Solution) {
                const sol = new solution.Solution();
                const method = Object.keys(sol).find(k => typeof sol[k] === 'function') ||
                    Object.keys(Object.getPrototypeOf(sol)).find(k => typeof sol[k] === 'function');
                result = sol[method](...parsedInputs);
            } else {
                const method = Object.keys(solution).find(k => typeof solution[k] === 'function');
                result = solution[method](...parsedInputs);
            }

            const resultSerialized = (result instanceof ListNode || result instanceof TreeNode) ? result.serialize() : result;
            const ok = JSON.stringify(resultSerialized) === JSON.stringify(parsedExpected);

            const status = ok ? '\x1b[32mPASSED\x1b[0m' : '\x1b[31mFAILED\x1b[0m';
            console.log(`${status} Test ${index + 1}: args ${JSON.stringify(parsedInputs)} result ${JSON.stringify(resultSerialized)} expected ${JSON.stringify(parsedExpected)}`);
        } catch (e) {
            console.log(`\x1b[31mERROR\x1b[0m Test ${index + 1}: ${e.message}`);
        }
    });
}

class ListNode {
    constructor(val, next) {
        this.val = (val === undefined ? 0 : val);
        this.next = (next === undefined ? null : next);
    }
    serialize() {
        let res = [];
        let curr = this;
        while (res.length < 100 && curr) {
            res.push(curr.val);
            curr = curr.next;
        }
        return res;
    }
}

class TreeNode {
    constructor(val, left, right) {
        this.val = (val === undefined ? 0 : val);
        this.left = (left === undefined ? null : left);
        this.right = (right === undefined ? null : right);
    }
    serialize() {
        let res = [];
        let q = [this];
        while (q.length > 0) {
            let node = q.shift();
            if (node) {
                res.push(node.val);
                q.push(node.left);
                q.push(node.right);
            } else {
                res.push(null);
            }
        }
        while (res[res.length - 1] === null) res.pop();
        return res;
    }
}

module.exports = { ListNode, TreeNode, runTest };
