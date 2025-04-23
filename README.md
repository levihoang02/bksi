## Service Configuration Table

| Service Name      | Internal Port | Publish Port | Protocol | Description                                                           |
| ----------------- | ------------- | ------------ | -------- | --------------------------------------------------------------------- |
| zookeeper         | 2181          | 8222         | TCP      | Zookeeper Port for Kafka                                              |
| kafka-1           | 9092          | 8200         | TCP      | Cổng giao tiếp với kafka broker 01 trên listener EXTERNAL             |
| kafka-1           | 29092         | 8201         | TCP      | Cổng giao tiếp với kafka broker 01 trên listener DOCKER               |
| kafka-2           | 9093          | 8202         | TCP      | Cổng giao tiếp với kafka broker 02 trên listener EXTERNAL             |
| kafka-2           | 29093         | 8203         | TCP      | Cổng giao tiếp với kafka broker 02 trên listener DOCKER               |
| kafka-3           | 9094          | 8204         | TCP      | Cổng giao tiếp với kafka broker 03 trên listener EXTERNAL             |
| kafka-3           | 29094         | 8205         | TCP      | Cổng giao tiếp với kafka broker 03 trên listener DOCKER               |
| kafdrop1          | 9000          | 8206         | HTTP     | Cổng truy cập giao diện quản lý kafka brokers                         |
| redis             | 6369          | 8207         | TCP      | Cổng kết nối redis server                                             |
| mongodb           | 27107         | 8208         | TCP      | Cổng kết nối mongodb                                                  |
| prometheus        | 9090          | 8209         | HTTP     | Cổng kết nối & giao diện prometheus                                   |
| alertmanager      | 9095          | 8210         | HTTP     | Cổng kết nối & giao diện alert manager                                |
| healthcheck       | 8001          | 8220         | HTTP     | Cổng giao tiếp healthcheck - alert manager + xác nhận cảnh báo từ URL |
| dashboard         | 8081          | None         | HTTP     | Cổng giao tiếp nội bộ với service tạo dashboard                       |
| grafana           | 3000          | 8211         | HTTP     | Grafana UI Web                                                        |
| connect           | 8083          | 8012         | TCP      | Cổng giao tiếp với Debezium                                           |
| ticket-service    | 8080          | None         | HTTP     | Cổng giao tiếp với dịch vụ truy xuất ticket                           |
| management-module | 3200          | None         | HTTP     | Cổng giao tiếp với dịch vụ đăng ký service                            |
| report-service    | 5000          | None         | HTTP     | Cổng giao tiếp với dịch vụ quản lí feedback                           |
| api-gateway       | 8210          | 8215         | HTTP     | Cổng giao tiếp với API-Gateway                                        |
