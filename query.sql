WITH CTE AS (
  SELECT *, ROW_NUMBER() over (PARTITION BY High, Hour ORDER BY Name, Hour, Timestamp) AS rn FROM (
    SELECT upper(db1.Name) AS Name, round(db1.High,2) AS High, db1.Hour as Hour, ts AS Timestamp FROM (
      SELECT name AS Name, max(high) AS High, substring(ts,12,2) AS Hour FROM  "04" 
      GROUP BY 1, 3
      ORDER BY 1, 3
      ) db1, "04" db2
    WHERE db1.Name = db2.name AND db1.Hour = substring(ts,12,2) AND db1.high = db2.High
    ORDER BY Name, Hour) db3)
    SELECT Name, High, Hour, Timestamp,
    Case
    when rn=1 then (SELECT count(*) FROM CTE t1 WHERE t1.High = t2.High AND t1.Hour = t2.Hour)
    else 0
    end AS Recurrence
    FROM CTE t2 ORDER BY Name, Hour, Timestamp
