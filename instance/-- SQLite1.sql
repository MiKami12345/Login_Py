-- SQLite
SELECT U.id, U.username, U.password, T.description
FROM user AS U LEFT JOIN task AS T
ON U.id = T.user_id