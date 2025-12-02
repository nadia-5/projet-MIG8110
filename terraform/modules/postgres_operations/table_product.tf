resource "postgresql_script" "product" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS product cascade;
    EOT
    ,
    <<-EOT
create table product (
    product_id uuid primary key,
    product_category_id integer,
    name_length integer,
    description_length integer,
    photos_qty integer,
    weight_g integer,
    length_cm integer,
    height_cm integer,
    width_cm integer,
    inserted_at timestamp not null default CURRENT_TIMESTAMP,
    updated_at timestamp,
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
    ,    <<-EOT
    -- Attachement du trigger
    DROP TRiGGER IF EXISTS update_product_modtime ON product;
    CREATE TRIGGER update_product_modtime
    BEFORE UPDATE ON product
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    EOT
  ]
  depends_on = [ postgresql_script.product_category  , postgresql_script.trigger_function ]
}
