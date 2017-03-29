USE `torque`;

DROP TABLE IF EXISTS `raw_logs`;
CREATE TABLE `raw_logs` (
  `v` varchar(1) NOT NULL,
  `session` varchar(15) NOT NULL,
  `id` varchar(32) NOT NULL,
  `time` varchar(15) NOT NULL,
  `kff1005` float NOT NULL DEFAULT '0',
  `kff1006` float NOT NULL DEFAULT '0',
  `kff1001` float NOT NULL DEFAULT '0' COMMENT 'Speed (GPS)',
  `kff1007` float NOT NULL DEFAULT '0' COMMENT 'GPS Bearing',
  `k4` float NOT NULL DEFAULT '0' COMMENT 'Engine Load',
  `k2f` float NOT NULL DEFAULT '0' COMMENT 'Fuel Level',
  `k11` float NOT NULL DEFAULT '0' COMMENT 'Throttle Position',
  `k5` float NOT NULL DEFAULT '0' COMMENT 'Engine Coolant Temp',
  `kc` float NOT NULL DEFAULT '0' COMMENT 'Engine RPM',
  `kd` float NOT NULL DEFAULT '0' COMMENT 'Speed (OBD)',
  `kf` float NOT NULL DEFAULT '0' COMMENT 'Intake Air Temp',
  `kff1226` float NOT NULL DEFAULT '0' COMMENT 'Horsepower',
  `kff1220` float NOT NULL DEFAULT '0' COMMENT 'Accel (X)',
  `kff1221` float NOT NULL DEFAULT '0' COMMENT 'Accel (Y)',
  `k46` float NOT NULL DEFAULT '0' COMMENT 'Ambiant Air Temp',
  KEY `session` (`session`,`id`),
  KEY `id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;



{"kff1007": "0.0", "eml": "korostelevm@gmail.com", "kff1005": "-75.03767108", "time": "1490355689680", "kff1001": "0.0", "kff1223": "-4.3533798E-4", "session": "1490355683347", "kff1006": "40.11728256", "v": "8", "id": "613120cb5d93864dddd4ff73a32a28fe"}
setting headers!!!
get
{"profileVe": "85.0", "eml": "korostelevm@gmail.com", "time": "1490355689679", "profileWeight": "1400.0", "profileFuelCost": "0.84", "session": "1490355683347", "v": "8", "profileFuelType": "0", "profileName": "Not Setup", "id": "613120cb5d93864dddd4ff73a32a28fe"}
setting headers!!!
get
{"userUnitff1223": "g", "userUnitff1006": "\u00c2\u00b0", "eml": "korostelevm@gmail.com", "userUnitff1005": "\u00c2\u00b0", "userUnitff1001": "mph", "session": "1490355683347", "time": "1490355689680", "userUnitff1007": "", "v": "8", "userFullNameff1223": "Acceleration Sensor(Total)", "userShortNameff1223": "Accel", "id": "613120cb5d93864dddd4ff73a32a28fe"}
setting headers!!!
get
{"defaultUnitff1001": "km/h", "defaultUnitff1007": "", "defaultUnitff1006": "\u00c2\u00b0", "defaultUnitff1005": "\u00c2\u00b0", "eml": "korostelevm@gmail.com", "time": "1490355689680", "session": "1490355683347", "defaultUnitff1223": "g", "v": "8", "id": "613120cb5d93864dddd4ff73a32a28fe"}
setting headers!!!
get
{"kff1007": "0.0", "eml": "korostelevm@gmail.com", "kff1005": "-75.03766061", "time": "1490355690659", "kff1001": "0.0", "kff1223": "0.00250129", "session": "1490355683347", "kff1006": "40.11728408", "v": "8", "id": "613120cb5d93864dddd4ff73a32a28fe"}
setting headers!!!
get
{"kff1007": "0.0", "eml": "korostelevm@gmail.com", "kff1005": "-75.03766819", "time": "1490355691659", "kff1001": "0.0", "kff1223": "-0.0014712429", "session": "1490355683347", "kff1006": "40.1172863", "v": "8", "id": "613120cb5d93864dddd4ff73a32a28fe"}
setting headers!!!
get
{"kff1007": "0.0", "eml": "korostelevm@gmail.com", "kff1005": "-75.03767222", "time": "1490355692658", "kff1001": "0.0", "kff1223": "-0.014008267", "session": "1490355683347", "kff1006": "40.11729087", "v": "8", "id": "613120cb5d93864dddd4ff73a32a28fe"}

# torque_pro_server
