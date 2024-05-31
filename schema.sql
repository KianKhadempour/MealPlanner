CREATE TABLE `tags`(
    `id`    INT UNSIGNED NOT NULL PRIMARY KEY,
    `likes` INT NOT NULL
);
CREATE TABLE `recipes`(
    `id`   INT UNSIGNED NOT NULL PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL
);
CREATE TABLE `recipe_tags`(
    `recipe_id`   INT UNSIGNED NOT NULL,
    `tag_id`  INT UNSIGNED NOT NULL,
    FOREIGN KEY(`recipe_id`) REFERENCES recipes(`id`),
    FOREIGN KEY(`tag_id`) REFERENCES tags(`id`)
);
