/*
 Navicat Premium Data Transfer

 Source Server         : tt
 Source Server Type    : SQLite
 Source Server Version : 3017000
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3017000
 File Encoding         : 65001

 Date: 18/11/2025 20:55:09
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for chenxing
-- ----------------------------
DROP TABLE IF EXISTS "chenxing";
CREATE TABLE "chenxing" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "code" TEXT,
  "cx_code" TEXT,
  "name" TEXT,
  "cate" TEXT
);

-- ----------------------------
-- Auto increment value for chenxing
-- ----------------------------
UPDATE "sqlite_sequence" SET seq = 1 WHERE name = 'chenxing';

PRAGMA foreign_keys = true;
