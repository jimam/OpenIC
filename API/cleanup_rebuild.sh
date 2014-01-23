rm openic.db
cat create.sql | sqlite3 openic.db
export GLOBIGNORE=static/Profile_IM/new_user_im.png
rm -r static/Profile_IM/*
export GLOBIGNORE=
