# BagRoute

投递装袋：按路线订户顺序装袋，重量与体积双约束，超限拒收。路线可配置袋数上限，再开一袋会超上限时，当前及后续站点一律以「袋数用尽」拒收，已装袋保持不变。

## 启动

```bash
docker compose up --build
```

| 服务 | 地址 |
| --- | --- |
| 前端 | http://localhost:4300 |
| API | http://localhost:9300 |
| API 文档 | http://localhost:9300/docs |
| Postgres | localhost:5444 |

健康检查：`GET http://localhost:9300/api/health`

## 页面

- `/routes` — 路线
- `/stops` — 订户点
- `/pack` — 装袋
- `/bags` — 袋明细
- `/rejects` — 拒收
- `/weights` — 袋重

## 使用说明

1. 查看路线与订户点顺序；路线页可修改袋数上限（留空为不限）。
2. 在装袋页选择路线执行双约束装袋，页面显示本路线袋数上限。
3. 袋明细与袋重查看结果，拒收页查看超限订户（超重/超体积与袋数用尽分档）。

## 开发与测试

```bash
docker compose exec api pytest -q
```
