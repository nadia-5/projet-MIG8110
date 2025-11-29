resource "postgresql_script" "dim_product" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS dim_product cascade;
    EOT
    ,
    <<-EOT
create table dim_product (
    product_id integer primary key,
    product_category varchar,
    name_length integer,
    description_length integer,
    photos_qty integer,
    weight_g integer,
    length_cm integer,
    height_cm integer,
    width_cm integer,
    valid_from timestamp not null,
    valid_to timestamp,
    is_current boolean not null,
    rowhash varchar(64) not null,
    constraint chk_product_name_length check (name_length is null or name_length >= 0),
    constraint chk_product_description_length check (description_length is null or description_length >= 0),
    constraint chk_product_photos_qty check (photos_qty is null or photos_qty >= 0),
    constraint chk_product_weight_g check (weight_g is null or weight_g >= 0),
    constraint chk_product_length_cm check (length_cm is null or length_cm >= 0),
    constraint chk_product_height_cm check (height_cm is null or height_cm >= 0),
    constraint chk_product_width_cm check (width_cm is null or width_cm >= 0),
);
    EOT
  ]
}
