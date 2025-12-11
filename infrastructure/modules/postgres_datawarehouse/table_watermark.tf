resource "postgresql_script" "watermark" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS watermark cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE watermark (
        source_name VARCHAR(100) NOT NULL,
        destination_name VARCHAR(100) NOT NULL,
        watermark_column VARCHAR(100) NOT NULL,
        last_value timestamp,
        PRIMARY KEY (source_name, destination_name)
    );
    EOT
  ]
}
