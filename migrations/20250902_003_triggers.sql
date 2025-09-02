-- Function to auto-update updated_at
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
DECLARE
  tbl RECORD;
BEGIN
  FOR tbl IN
    SELECT tablename FROM pg_tables WHERE schemaname = 'public'
  LOOP
    EXECUTE format('
      CREATE TRIGGER set_updated_at_%I
      BEFORE UPDATE ON %I
      FOR EACH ROW
      EXECUTE FUNCTION set_updated_at();',
      tbl.tablename, tbl.tablename);
  END LOOP;
END;
$$;
