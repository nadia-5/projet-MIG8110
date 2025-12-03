resource "postgresql_script" "dim_date" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS dim_date cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE dim_date (
        date_id uuid PRIMARY KEY,
        date_value date NOT NULL,
        year integer NOT NULL,
        quarter integer NOT NULL,
        month integer NOT NULL,
        day integer NOT NULL,
        week_of_year integer NOT NULL,
        day_of_week integer NOT NULL,
        is_weekend boolean NOT NULL,
        rowhash varchar(64) not null
    );
    EOT
  ]
}