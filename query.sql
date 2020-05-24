SELECT upper(name) as Name, round(high,2) as High, timestamp as Timestamp, hour as Hour
from(
  select db.*,SUBSTRING(timestamp, 12, 2) as Hour, ROW_NUMBER() OVER(PARTITION BY name, SUBSTRING(timestamp, 12, 2) order by high) as rn
  FROM "21" db
  where timestamp between '05/14/2020 09:30:00' AND '05/14/2020 16:00:00'
)db1 where rn=1 order by name, timestamp