#include <iostream>
#include <cstring>
#include <set>
#include <unordered_map>
#include <unistd.h>
using namespace std;

const int N = 1e5;

// head 邻接表头，vertex存的顶点，next_p 存邻接表下一条边， idx 指针
int head[N], vertex[N], next_p[N], idx;
int n, m, ans = 1e9;
// colors[c] = {} 染成颜色 c 的点的集合
unordered_map<int, set<int>> colors;
unordered_map<int, set<int>> result;

//邻接表加边
void add(int a, int b)
{
    vertex[idx] = b, next_p[idx] = head[a], head[a] = idx++;
}

// 检查当前点 cur 能否染成 color 色
bool check(int cur, int color)
{
    for (int i = head[cur]; i != -1; i = next_p[i])
    {
        int target = vertex[i]; // cur 的邻点

        if (colors[color].find(target) != colors[color].end())
            return false;
    }

    return true;
}

// cur 当前点， color_num 颜色数
void draw(int cur, int color_num)
{
    if (color_num >= ans)
        return; //剪枝

    if (cur > n)
    {
        ans = min(ans, color_num); // 取最小的颜色方案数
        for (int i = 1; i <= color_num; i++)
        {
            result[i] = colors[i];
        }
        return;
    }

    // 依次枚举颜色
    for (int c = 1; c <= color_num; c++)
    {
        if (check(cur, c)) // 当前点 是否 能染成颜色 c
        {
            colors[c].insert(cur);
            draw(cur + 1, color_num); //不扩充颜色，染下一个点
            colors[c].erase(cur);
        }
    }

    colors[color_num + 1].insert(cur);
    draw(cur + 1, color_num + 1); // 扩充颜色，染下一个点
    colors[color_num + 1].erase(cur);
}

int main()
{
    cin >> n >> m;
    memset(head, -1, sizeof head);
    for (int i = 0; i < m; i++)
    {
        int a, b;
        cin >> a >> b;
        add(a, b);
        add(b, a);
    }

    draw(1, 0);

    // for (auto kv = result.begin(); kv != result.end(); kv ++)
    // {
    //     cout << "color " << kv->first << " : ";
    //     for (auto item = kv->second.begin(); item != kv->second.end(); item ++)
    //         cout << *item << ' ';
    //     cout << endl;
    // }

    cout << ans << endl;

    return 0;
}