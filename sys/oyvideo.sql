
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

--
-- База данных: `oyvideo`
--

-- --------------------------------------------------------

--
-- Структура таблицы `channels`
--

CREATE TABLE `channels` (
  `id` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL,
  `idx` int(11) NOT NULL DEFAULT 1,
  `ctime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `oyids`
--

CREATE TABLE `oyids` (
  `serial` int(11) NOT NULL,
  `oyid` varchar(255) NOT NULL,
  `ctime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `playlists`
--

CREATE TABLE `playlists` (
  `id` varchar(255) NOT NULL,
  `place` enum('archive','vk','youtube') NOT NULL,
  `channel_id` varchar(255) DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `status` set('error','checked') DEFAULT NULL,
  `ctime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `playlists_members`
--

CREATE TABLE `playlists_members` (
  `playlist_id` varchar(255) NOT NULL,
  `video_id` varchar(255) NOT NULL,
  `position` int(11) NOT NULL,
  `status` set('error','ok') DEFAULT NULL,
  `ctime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `videos`
--

CREATE TABLE `videos` (
  `id` varchar(255) NOT NULL,
  `oyid` varchar(255) NOT NULL,
  `place` enum('archive','vk','old.openyogaclass.com','youtube') NOT NULL,
  `channel` varchar(255) DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `main_filename` varchar(255) DEFAULT NULL,
  `video_md5` varchar(255) NOT NULL,
  `lang` varchar(255) DEFAULT NULL,
  `license` varchar(255) DEFAULT NULL,
  `storage` varchar(255) DEFAULT NULL,
  `status` set('checked','downloaded','uploaded') DEFAULT NULL,
  `ctime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `youtube_files_name`
--

CREATE TABLE `youtube_files_name` (
  `channel_id` varchar(255) NOT NULL,
  `video_id` varchar(255) NOT NULL,
  `file_name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `channels`
--
ALTER TABLE `channels`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `oyids`
--
ALTER TABLE `oyids`
  ADD PRIMARY KEY (`serial`),
  ADD UNIQUE KEY `oyid` (`oyid`);

--
-- Индексы таблицы `playlists`
--
ALTER TABLE `playlists`
  ADD PRIMARY KEY (`id`(40),`place`) USING BTREE;

--
-- Индексы таблицы `playlists_members`
--
ALTER TABLE `playlists_members`
  ADD KEY `playlist_id` (`playlist_id`);

--
-- Индексы таблицы `videos`
--
ALTER TABLE `videos`
  ADD KEY `oyid` (`oyid`),
  ADD KEY `id` (`id`);

--
-- Индексы таблицы `youtube_files_name`
--
ALTER TABLE `youtube_files_name`
  ADD PRIMARY KEY (`video_id`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `oyids`
--
ALTER TABLE `oyids`
  MODIFY `serial` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;
