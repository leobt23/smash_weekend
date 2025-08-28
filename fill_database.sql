INSERT INTO groups (group_name) VALUES
('A'),
('B'),
('C'),
('D');

INSERT INTO teams (team_name, player1, player2, top_seeded) VALUES
('André Andrade / Francisco Zagalo', 'André Andrade', 'Francisco Zagalo', TRUE),
('Nuno Silva / Gonçalo Silva', 'Nuno Silva', 'Gonçalo Silva', FALSE),
('David Miranda / Hugo Mendonça', 'David Miranda', 'Hugo Mendonça', FALSE),

('Leonel Mendes / Ricardo Oliveira', 'Leonel Mendes', 'Ricardo Oliveira', TRUE),
('Diogo Mota / Gonçalo Santos', 'Diogo Mota', 'Gonçalo Santos', FALSE),
('Guilherme Brito / Guilherme Amaral', 'Guilherme Brito', 'Guilherme Amaral', FALSE),

('Flávio Fonseca / Ricky Duarte', 'Flávio Fonseca', 'Ricky Duarte', FALSE),
('Cédric Dias / Leonardo Brito', 'Cédric Dias', 'Leonardo Brito', TRUE),
('Jorge Cruz / Miguel Lucena', 'Jorge Cruz', 'Miguel Lucena', FALSE),

('Gonçalo Castanheira / André Castanheira', 'Gonçalo Castanheira', 'André Castanheira', FALSE),
('Emanuel António / Carlos Martins', 'Emanuel António', 'Carlos Martins', FALSE),
('João Fernandes / Pedro Félix', 'João Fernandes', 'Pedro Félix', TRUE);

-- Grupo A
INSERT INTO group_teams (group_id, team_id) VALUES
(1, 1), (1, 2), (1, 3);

-- Grupo B
INSERT INTO group_teams (group_id, team_id) VALUES
(2, 4), (2, 5), (2, 6);

-- Grupo C
INSERT INTO group_teams (group_id, team_id) VALUES
(3, 7), (3, 8), (3, 9);

-- Grupo D
INSERT INTO group_teams (group_id, team_id) VALUES
(4, 10), (4, 11), (4, 12);

-- QUINTA
INSERT INTO matches (group_id, team1_id, team2_id, match_time, match_location, match_status) VALUES
(2, 5, 4, '2025-08-28 21:00:00', 'Pizzaria Papo-Seco', 'scheduled'),
(3, 7, 8, '2025-08-28 21:00:00', 'Velmar', 'scheduled'),
(3, 9, 8, '2025-08-28 22:00:00', 'Pizzaria Papo-Seco', 'scheduled'),
(4, 10, 11, '2025-08-28 22:00:00', 'Velmar', 'scheduled');

-- SEXTA
INSERT INTO matches (group_id, team1_id, team2_id, match_time, match_location, match_status) VALUES
(1, 1, 2, '2025-08-29 18:15:00', 'Pizzaria Papo-Seco', 'scheduled'),
(2, 6, 4, '2025-08-29 19:15:00', 'Velmar', 'scheduled'),
(4, 10, 12, '2025-08-29 19:15:00', 'Velmar', 'scheduled'),
(1, 1, 3, '2025-08-29 20:15:00', 'Pizzaria Papo-Seco', 'scheduled'),
(4, 11, 12, '2025-08-29 21:15:00', 'Pizzaria Papo-Seco', 'scheduled'),
(2, 5, 6, '2025-08-29 21:15:00', 'Velmar', 'scheduled'),
(1, 2, 3, '2025-08-29 22:15:00', 'Pizzaria Papo-Seco', 'scheduled'),
(3, 7, 9, '2025-08-29 22:15:00', 'Velmar', 'scheduled');

INSERT INTO matches (group_id, team1_id, team2_id, match_time, match_location, match_status, set1_team1, set1_team2, set2_team1, set2_team2, winner_team_id) VALUES
(1, 1, 2, '2025-08-25 10:15:00', 'Pizzaria Papo-Seco', 'finished', 7, 6, 6, 3, 1);