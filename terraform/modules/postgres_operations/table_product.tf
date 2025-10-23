resource "postgresql_script" "product" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS product;
    EOT
    ,
    <<-EOT
create table product (
    product_id varchar(255) primary key,
    product_category_id integer,
    name_length integer,
    description_length integer,
    photos_qty integer,
    weight_g integer,
    length_cm integer,
    height_cm integer,
    width_cm integer,
    constraint chk_product_name_length check (name_length is null or name_length >= 0),
    constraint chk_product_description_length check (description_length is null or description_length >= 0),
    constraint chk_product_photos_qty check (photos_qty is null or photos_qty >= 0),
    constraint chk_product_weight_g check (weight_g is null or weight_g >= 0),
    constraint chk_product_length_cm check (length_cm is null or length_cm >= 0),
    constraint chk_product_height_cm check (height_cm is null or height_cm >= 0),
    constraint chk_product_width_cm check (width_cm is null or width_cm >= 0),
    foreign key (product_category_id) references product_category(product_category_id)
);
    EOT
  ]
  depends_on = [ postgresql_script.product_category ]
}
