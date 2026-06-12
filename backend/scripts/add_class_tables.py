# Script: add structured table data to clases_razas.json
# Run: python scripts/add_class_tables.py

import json

TABLE_DATA = {
    "Bárbaro": {
        "columnas": ["Nivel", "Bon. por competencia", "Rasgos", "N.º de furias", "Daño por furia"],
        "filas": [
            ["1", "+2", "Furia, Defensa sin Armadura", "2", "+2"],
            ["2", "+2", "Ataque Temerario, Sentir el Peligro", "2", "+2"],
            ["3", "+2", "Senda Primordial", "3", "+2"],
            ["4", "+2", "Mejora de Característica", "3", "+2"],
            ["5", "+3", "Ataque Adicional, Movimiento Rápido", "3", "+2"],
            ["6", "+3", "Rasgo de Senda", "4", "+2"],
            ["7", "+3", "Instinto Salvaje", "4", "+2"],
            ["8", "+3", "Mejora de Característica", "4", "+2"],
            ["9", "+4", "Crítico Brutal (1 dado)", "4", "+3"],
            ["10", "+4", "Rasgo de Senda", "4", "+3"],
            ["11", "+4", "Furia Implacable", "4", "+3"],
            ["12", "+4", "Mejora de Característica", "5", "+3"],
            ["13", "+5", "Crítico Brutal (2 dados)", "5", "+3"],
            ["14", "+5", "Rasgo de Senda", "5", "+3"],
            ["15", "+5", "Furia Persistente", "5", "+3"],
            ["16", "+5", "Mejora de Característica", "5", "+4"],
            ["17", "+6", "Crítico Brutal (3 dados)", "6", "+4"],
            ["18", "+6", "Poderío Indómito", "6", "+4"],
            ["19", "+6", "Mejora de Característica", "6", "+4"],
            ["20", "+6", "Campeón Primordial", "Ilimitadas", "+4"],
        ]
    },
    "Bardo": {
        "columnas": ["Nivel", "Bon. por competencia", "Rasgos", "Trucos conocidos", "Conjuros conocidos", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        "filas": [
            ["1", "+2", "Lanzamiento de Conjuros, Inspiración Bárdica (d6)", "2", "4", "2", "—", "—", "—", "—", "—", "—", "—", "—"],
            ["2", "+2", "Aprendiz de Mucho, Canción de Descanso (d6)", "2", "5", "3", "—", "—", "—", "—", "—", "—", "—", "—"],
            ["3", "+2", "Colegio Bárdico, Pericia", "2", "6", "4", "2", "—", "—", "—", "—", "—", "—", "—"],
            ["4", "+2", "Mejora de Característica", "3", "7", "4", "3", "—", "—", "—", "—", "—", "—", "—"],
            ["5", "+3", "Inspiración Bárdica (d8), Fuente de Inspiración", "3", "8", "4", "3", "2", "—", "—", "—", "—", "—", "—"],
            ["6", "+3", "Contraencantamiento, rasgo de Colegio Bárdico", "3", "9", "4", "3", "3", "—", "—", "—", "—", "—", "—"],
            ["7", "+3", "—", "3", "10", "4", "3", "3", "1", "—", "—", "—", "—", "—"],
            ["8", "+3", "Mejora de Característica", "3", "11", "4", "3", "3", "2", "—", "—", "—", "—", "—"],
            ["9", "+4", "Canción de Descanso (d8)", "3", "12", "4", "3", "3", "3", "1", "—", "—", "—", "—"],
            ["10", "+4", "Inspiración Bárdica (d10), Pericia, Secretos Mágicos", "4", "14", "4", "3", "3", "3", "2", "—", "—", "—", "—"],
            ["11", "+4", "—", "4", "15", "4", "3", "3", "3", "2", "1", "—", "—", "—"],
            ["12", "+4", "Mejora de Característica", "4", "15", "4", "3", "3", "3", "2", "1", "—", "—", "—"],
            ["13", "+5", "Canción de Descanso (d10)", "4", "16", "4", "3", "3", "3", "2", "1", "1", "—", "—"],
            ["14", "+5", "Secretos Mágicos, rasgo de Colegio Bárdico", "4", "18", "4", "3", "3", "3", "2", "1", "1", "—", "—"],
            ["15", "+5", "Inspiración Bárdica (d12)", "4", "19", "4", "3", "3", "3", "2", "1", "1", "1", "—"],
            ["16", "+5", "Mejora de Característica", "4", "19", "4", "3", "3", "3", "2", "1", "1", "1", "—"],
            ["17", "+6", "Canción de Descanso (d12)", "4", "20", "4", "3", "3", "3", "2", "1", "1", "1", "1"],
            ["18", "+6", "Secretos Mágicos", "4", "22", "4", "3", "3", "3", "3", "1", "1", "1", "1"],
            ["19", "+6", "Mejora de Característica", "4", "22", "4", "3", "3", "3", "3", "2", "1", "1", "1"],
            ["20", "+6", "Superioridad Inspiradora", "4", "24", "4", "3", "3", "3", "3", "2", "2", "1", "1"],
        ]
    },
    "Brujo": {
        "columnas": ["Nivel", "Bon. por competencia", "Rasgos", "Trucos conocidos", "Conjuros conocidos", "Espacios de conjuro", "Nivel de espacios", "Invocaciones conocidas"],
        "filas": [
            ["1", "+2", "Patrón Sobrenatural, Magia del Pacto", "2", "2", "1", "1", "—"],
            ["2", "+2", "Invocaciones Sobrenaturales", "2", "3", "2", "1", "2"],
            ["3", "+2", "Beneficio del Pacto", "2", "4", "2", "2", "2"],
            ["4", "+2", "Mejora de Característica", "3", "5", "2", "2", "2"],
            ["5", "+3", "—", "3", "6", "2", "3", "3"],
            ["6", "+3", "Rasgo de Patrón Sobrenatural", "3", "7", "2", "3", "3"],
            ["7", "+3", "—", "3", "8", "2", "4", "4"],
            ["8", "+3", "Mejora de Característica", "3", "9", "2", "4", "4"],
            ["9", "+4", "—", "3", "10", "2", "5", "5"],
            ["10", "+4", "Rasgo de Patrón Sobrenatural", "4", "10", "2", "5", "5"],
            ["11", "+4", "Arcano Místico (nivel 6)", "4", "11", "3", "5", "5"],
            ["12", "+4", "Mejora de Característica", "4", "11", "3", "5", "6"],
            ["13", "+5", "Arcano Místico (nivel 7)", "4", "12", "3", "5", "6"],
            ["14", "+5", "Rasgo de Patrón Sobrenatural", "4", "12", "3", "5", "6"],
            ["15", "+5", "Arcano Místico (nivel 8)", "4", "13", "3", "5", "7"],
            ["16", "+5", "Mejora de Característica", "4", "13", "3", "5", "7"],
            ["17", "+6", "Arcano Místico (nivel 9)", "4", "14", "4", "5", "7"],
            ["18", "+6", "Rasgo de Patrón Sobrenatural", "4", "14", "4", "5", "8"],
            ["19", "+6", "Mejora de Característica", "4", "15", "4", "5", "8"],
            ["20", "+6", "Eldritch Master", "4", "15", "4", "5", "8"],
        ]
    },
    "Clérigo": {
        "columnas": ["Nivel", "Bon. por competencia", "Rasgos", "Trucos conocidos", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        "filas": [
            ["1", "+2", "Lanzamiento de Conjuros, Dominio Divino", "3", "2", "—", "—", "—", "—", "—", "—", "—", "—"],
            ["2", "+2", "Canalizar Divinidad (1/descanso), rasgo de Dominio Divino", "3", "3", "—", "—", "—", "—", "—", "—", "—", "—"],
            ["3", "+2", "—", "3", "4", "2", "—", "—", "—", "—", "—", "—", "—"],
            ["4", "+2", "Mejora de Característica", "4", "4", "3", "—", "—", "—", "—", "—", "—", "—"],
            ["5", "+3", "Destruir Muertos Vivientes (VD 1/2)", "4", "4", "3", "2", "—", "—", "—", "—", "—", "—"],
            ["6", "+3", "Canalizar Divinidad (2/descanso), rasgo de Dominio Divino", "4", "4", "3", "3", "—", "—", "—", "—", "—", "—"],
            ["7", "+3", "—", "4", "4", "3", "3", "1", "—", "—", "—", "—", "—"],
            ["8", "+3", "Mejora de Característica, Destruir Muertos Vivientes (VD 1), rasgo de Dominio Divino", "4", "4", "3", "3", "2", "—", "—", "—", "—", "—"],
            ["9", "+4", "—", "4", "4", "3", "3", "3", "1", "—", "—", "—", "—"],
            ["10", "+4", "Intercesión Divina", "5", "4", "3", "3", "3", "2", "—", "—", "—", "—"],
            ["11", "+4", "Destruir Muertos Vivientes (VD 2)", "5", "4", "3", "3", "3", "2", "1", "—", "—", "—"],
            ["12", "+4", "Mejora de Característica", "5", "4", "3", "3", "3", "2", "1", "—", "—", "—"],
            ["13", "+5", "—", "5", "4", "3", "3", "3", "2", "1", "1", "—", "—"],
            ["14", "+5", "Destruir Muertos Vivientes (VD 3)", "5", "4", "3", "3", "3", "2", "1", "1", "—", "—"],
            ["15", "+5", "—", "5", "4", "3", "3", "3", "2", "1", "1", "1", "—"],
            ["16", "+5", "Mejora de Característica", "5", "4", "3", "3", "3", "2", "1", "1", "1", "—"],
            ["17", "+6", "—", "5", "4", "3", "3", "3", "2", "1", "1", "1", "1"],
            ["18", "+6", "Canalizar Divinidad (3/descanso), rasgo de Dominio Divino", "5", "4", "3", "3", "3", "3", "1", "1", "1", "1"],
            ["19", "+6", "Mejora de Característica", "5", "4", "3", "3", "3", "3", "2", "1", "1", "1"],
            ["20", "+6", "Intervención Divina (mejorada)", "5", "4", "3", "3", "3", "3", "2", "2", "1", "1"],
        ]
    },
    "Druida": {
        "columnas": ["Nivel", "Bon. por competencia", "Rasgos", "Trucos conocidos", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        "filas": [
            ["1", "+2", "Druídico, Lanzamiento de Conjuros", "2", "2", "—", "—", "—", "—", "—", "—", "—", "—"],
            ["2", "+2", "Forma Salvaje, Círculo Druídico", "2", "3", "—", "—", "—", "—", "—", "—", "—", "—"],
            ["3", "+2", "—", "2", "4", "2", "—", "—", "—", "—", "—", "—", "—"],
            ["4", "+2", "Mejora de Forma Salvaje, Mejora de Característica", "3", "4", "3", "—", "—", "—", "—", "—", "—", "—"],
            ["5", "+3", "—", "3", "4", "3", "2", "—", "—", "—", "—", "—", "—"],
            ["6", "+3", "Rasgo de Círculo Druídico", "3", "4", "3", "3", "—", "—", "—", "—", "—", "—"],
            ["7", "+3", "—", "3", "4", "3", "3", "1", "—", "—", "—", "—", "—"],
            ["8", "+3", "Mejora de Forma Salvaje, Mejora de Característica", "3", "4", "3", "3", "2", "—", "—", "—", "—", "—"],
            ["9", "+4", "—", "3", "4", "3", "3", "3", "1", "—", "—", "—", "—"],
            ["10", "+4", "Rasgo de Círculo Druídico", "4", "4", "3", "3", "3", "2", "—", "—", "—", "—"],
            ["11", "+4", "—", "4", "4", "3", "3", "3", "2", "1", "—", "—", "—"],
            ["12", "+4", "Mejora de Característica", "4", "4", "3", "3", "3", "2", "1", "—", "—", "—"],
            ["13", "+5", "—", "4", "4", "3", "3", "3", "2", "1", "1", "—", "—"],
            ["14", "+5", "Rasgo de Círculo Druídico", "4", "4", "3", "3", "3", "2", "1", "1", "—", "—"],
            ["15", "+5", "—", "4", "4", "3", "3", "3", "2", "1", "1", "1", "—"],
            ["16", "+5", "Mejora de Característica", "4", "4", "3", "3", "3", "2", "1", "1", "1", "—"],
            ["17", "+6", "—", "4", "4", "3", "3", "3", "2", "1", "1", "1", "1"],
            ["18", "+6", "Cuerpo Atemporal, Conjurar como Bestia", "4", "4", "3", "3", "3", "3", "1", "1", "1", "1"],
            ["19", "+6", "Mejora de Característica", "4", "4", "3", "3", "3", "3", "2", "1", "1", "1"],
            ["20", "+6", "Arquidruida", "4", "4", "3", "3", "3", "3", "2", "2", "1", "1"],
        ]
    },
    "Explorador": {
        "columnas": ["Nivel", "Bon. por competencia", "Rasgos", "Conjuros conocidos", "1", "2", "3", "4", "5"],
        "filas": [
            ["1", "+2", "Enemigo Predilecto, Explorador Nato", "—", "—", "—", "—", "—", "—"],
            ["2", "+2", "Estilo de Combate, Lanzamiento de Conjuros", "2", "2", "—", "—", "—", "—"],
            ["3", "+2", "Arquetipo de Explorador, Percepción Primigenia", "3", "3", "—", "—", "—", "—"],
            ["4", "+2", "Mejora de Característica", "3", "3", "—", "—", "—", "—"],
            ["5", "+3", "Ataque Adicional", "4", "4", "2", "—", "—", "—"],
            ["6", "+3", "Mejoras de Enemigo Predilecto y Explorador Nato", "4", "4", "2", "—", "—", "—"],
            ["7", "+3", "Rasgo de Arquetipo de Explorador", "5", "4", "3", "—", "—", "—"],
            ["8", "+3", "Mejora de Característica, Paso de la Tierra", "5", "4", "3", "—", "—", "—"],
            ["9", "+4", "—", "6", "4", "3", "2", "—", "—"],
            ["10", "+4", "Mejora de Explorador Nato, Esconderse a Plena Vista", "6", "4", "3", "2", "—", "—"],
            ["11", "+4", "Rasgo de Arquetipo de Explorador", "7", "4", "3", "3", "—", "—"],
            ["12", "+4", "Mejora de Característica", "7", "4", "3", "3", "—", "—"],
            ["13", "+5", "—", "8", "4", "3", "3", "1", "—"],
            ["14", "+5", "Mejora de Enemigo Predilecto, Desvanecerse", "8", "4", "3", "3", "1", "—"],
            ["15", "+5", "Rasgo de Arquetipo de Explorador", "9", "4", "3", "3", "2", "—"],
            ["16", "+5", "Mejora de Característica", "9", "4", "3", "3", "2", "—"],
            ["17", "+6", "—", "10", "4", "3", "3", "3", "1"],
            ["18", "+6", "Sentidos Salvajes", "10", "4", "3", "3", "3", "1"],
            ["19", "+6", "Mejora de Característica", "10", "4", "3", "3", "3", "2"],
            ["20", "+6", "Azote de Enemigos", "10", "4", "3", "3", "3", "2"],
        ]
    },
    "Guerrero": {
        "columnas": ["Nivel", "Bon. por competencia", "Rasgos"],
        "filas": [
            ["1", "+2", "Estilo de Combate, Tomar Aliento"],
            ["2", "+2", "Acción Súbita (un uso)"],
            ["3", "+2", "Arquetipo Marcial"],
            ["4", "+2", "Mejora de Característica"],
            ["5", "+3", "Ataque Adicional"],
            ["6", "+3", "Mejora de Característica"],
            ["7", "+3", "Rasgo de Arquetipo Marcial"],
            ["8", "+3", "Mejora de Característica"],
            ["9", "+4", "Indómito (un uso)"],
            ["10", "+4", "Rasgo de Arquetipo Marcial"],
            ["11", "+4", "Ataque Adicional (2)"],
            ["12", "+4", "Mejora de Característica"],
            ["13", "+5", "Indómito (dos usos)"],
            ["14", "+5", "Mejora de Característica"],
            ["15", "+5", "Rasgo de Arquetipo Marcial"],
            ["16", "+5", "Mejora de Característica"],
            ["17", "+6", "Acción Súbita (dos usos), Indómito (tres usos)"],
            ["18", "+6", "Rasgo de Arquetipo Marcial"],
            ["19", "+6", "Mejora de Característica"],
            ["20", "+6", "Ataque Adicional (3)"],
        ]
    },
    "Hechicero": {
        "columnas": ["Nivel", "Bon. por competencia", "Puntos de hechicería", "Rasgos", "Trucos conocidos", "Conjuros conocidos", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        "filas": [
            ["1", "+2", "—", "Lanzamiento de Conjuros, Origen Mágico", "4", "2", "2", "—", "—", "—", "—", "—", "—", "—", "—"],
            ["2", "+2", "2", "Fuente de Magia", "4", "3", "3", "—", "—", "—", "—", "—", "—", "—", "—"],
            ["3", "+2", "3", "Metamagia", "4", "4", "4", "2", "—", "—", "—", "—", "—", "—", "—"],
            ["4", "+2", "4", "Mejora de Característica", "5", "5", "4", "3", "—", "—", "—", "—", "—", "—", "—"],
            ["5", "+3", "5", "—", "5", "6", "4", "3", "2", "—", "—", "—", "—", "—", "—"],
            ["6", "+3", "6", "Rasgo de Origen Mágico", "5", "7", "4", "3", "3", "—", "—", "—", "—", "—", "—"],
            ["7", "+3", "7", "—", "5", "8", "4", "3", "3", "1", "—", "—", "—", "—", "—"],
            ["8", "+3", "8", "Mejora de Característica", "5", "9", "4", "3", "3", "2", "—", "—", "—", "—", "—"],
            ["9", "+4", "9", "—", "5", "10", "4", "3", "3", "3", "1", "—", "—", "—", "—"],
            ["10", "+4", "10", "Metamagia", "6", "11", "4", "3", "3", "3", "2", "—", "—", "—", "—"],
            ["11", "+4", "11", "—", "6", "12", "4", "3", "3", "3", "2", "1", "—", "—", "—"],
            ["12", "+4", "12", "Mejora de Característica", "6", "12", "4", "3", "3", "3", "2", "1", "—", "—", "—"],
            ["13", "+5", "13", "—", "6", "13", "4", "3", "3", "3", "2", "1", "1", "—", "—"],
            ["14", "+5", "14", "Rasgo de Origen Mágico", "6", "13", "4", "3", "3", "3", "2", "1", "1", "—", "—"],
            ["15", "+5", "15", "—", "6", "14", "4", "3", "3", "3", "2", "1", "1", "1", "—"],
            ["16", "+5", "16", "Mejora de Característica", "6", "14", "4", "3", "3", "3", "2", "1", "1", "1", "—"],
            ["17", "+6", "17", "Metamagia", "6", "15", "4", "3", "3", "3", "2", "1", "1", "1", "1"],
            ["18", "+6", "18", "Rasgo de Origen Mágico", "6", "15", "4", "3", "3", "3", "3", "1", "1", "1", "1"],
            ["19", "+6", "19", "Mejora de Característica", "6", "15", "4", "3", "3", "3", "3", "2", "1", "1", "1"],
            ["20", "+6", "20", "Recuperación Mágica", "6", "15", "4", "3", "3", "3", "3", "2", "2", "1", "1"],
        ]
    },
    "Mago": {
        "columnas": ["Nivel", "Bon. por competencia", "Rasgos", "Trucos conocidos", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        "filas": [
            ["1", "+2", "Lanzamiento de Conjuros, Recuperación Arcana", "3", "2", "—", "—", "—", "—", "—", "—", "—", "—"],
            ["2", "+2", "Tradición Arcana", "3", "3", "—", "—", "—", "—", "—", "—", "—", "—"],
            ["3", "+2", "—", "3", "4", "2", "—", "—", "—", "—", "—", "—", "—"],
            ["4", "+2", "Mejora de Característica", "4", "4", "3", "—", "—", "—", "—", "—", "—", "—"],
            ["5", "+3", "—", "4", "4", "3", "2", "—", "—", "—", "—", "—", "—"],
            ["6", "+3", "Rasgo de Tradición Arcana", "4", "4", "3", "3", "—", "—", "—", "—", "—", "—"],
            ["7", "+3", "—", "4", "4", "3", "3", "1", "—", "—", "—", "—", "—"],
            ["8", "+3", "Mejora de Característica", "4", "4", "3", "3", "2", "—", "—", "—", "—", "—"],
            ["9", "+4", "—", "4", "4", "3", "3", "3", "1", "—", "—", "—", "—"],
            ["10", "+4", "Rasgo de Tradición Arcana", "5", "4", "3", "3", "3", "2", "—", "—", "—", "—"],
            ["11", "+4", "—", "5", "4", "3", "3", "3", "2", "1", "—", "—", "—"],
            ["12", "+4", "Mejora de Característica", "5", "4", "3", "3", "3", "2", "1", "—", "—", "—"],
            ["13", "+5", "—", "5", "4", "3", "3", "3", "2", "1", "1", "—", "—"],
            ["14", "+5", "Rasgo de Tradición Arcana", "5", "4", "3", "3", "3", "2", "1", "1", "—", "—"],
            ["15", "+5", "—", "5", "4", "3", "3", "3", "2", "1", "1", "1", "—"],
            ["16", "+5", "Mejora de Característica", "5", "4", "3", "3", "3", "2", "1", "1", "1", "—"],
            ["17", "+6", "—", "5", "4", "3", "3", "3", "2", "1", "1", "1", "1"],
            ["18", "+6", "Maestría sobre Conjuros", "5", "4", "3", "3", "3", "3", "1", "1", "1", "1"],
            ["19", "+6", "Mejora de Característica", "5", "4", "3", "3", "3", "3", "2", "1", "1", "1"],
            ["20", "+6", "Conjuro Característico", "5", "4", "3", "3", "3", "3", "2", "2", "1", "1"],
        ]
    },
    "Monje": {
        "columnas": ["Nivel", "Bon. por competencia", "Artes marciales", "Puntos de ki", "Movimiento sin Armadura", "Rasgos"],
        "filas": [
            ["1", "+2", "1d4", "—", "—", "Defensa sin Armadura, Artes Marciales"],
            ["2", "+2", "1d4", "2", "+3 m", "Ki, Movimiento sin Armadura"],
            ["3", "+2", "1d4", "3", "+3 m", "Tradición Monástica, Desviar Proyectiles"],
            ["4", "+2", "1d4", "4", "+3 m", "Mejora de Característica, Caída Lenta"],
            ["5", "+3", "1d6", "5", "+3 m", "Ataque Adicional, Golpe Aturdidor"],
            ["6", "+3", "1d6", "6", "+4,5 m", "Golpes Potenciados con Ki, rasgo de Tradición Monástica"],
            ["7", "+3", "1d6", "7", "+4,5 m", "Evasión, Quietud Mental"],
            ["8", "+3", "1d6", "8", "+4,5 m", "Mejora de Característica"],
            ["9", "+4", "1d6", "9", "+4,5 m", "Mejora de Movimiento sin Armadura"],
            ["10", "+4", "1d6", "10", "+6 m", "Pureza de Cuerpo"],
            ["11", "+4", "1d8", "11", "+6 m", "Rasgo de Tradición Monástica"],
            ["12", "+4", "1d8", "12", "+6 m", "Mejora de Característica"],
            ["13", "+5", "1d8", "13", "+6 m", "Lengua del Sol y la Luna"],
            ["14", "+5", "1d8", "14", "+7,5 m", "Alma Diamantina"],
            ["15", "+5", "1d8", "15", "+7,5 m", "Cuerpo Atemporal"],
            ["16", "+5", "1d8", "16", "+7,5 m", "Mejora de Característica"],
            ["17", "+6", "1d10", "17", "+7,5 m", "Rasgo de Tradición Monástica"],
            ["18", "+6", "1d10", "18", "+9 m", "Cuerpo Vacío"],
            ["19", "+6", "1d10", "19", "+9 m", "Mejora de Característica"],
            ["20", "+6", "1d10", "20", "+9 m", "Yo Perfecto"],
        ]
    },
    "Paladín": {
        "columnas": ["Nivel", "Bon. por competencia", "Rasgos", "1", "2", "3", "4", "5"],
        "filas": [
            ["1", "+2", "Sentidos Divinos, Imponer las Manos", "—", "—", "—", "—", "—"],
            ["2", "+2", "Estilo de Combate, Lanzamiento de Conjuros, Castigo Divino", "2", "—", "—", "—", "—"],
            ["3", "+2", "Salud Divina, Juramento Sagrado", "3", "—", "—", "—", "—"],
            ["4", "+2", "Mejora de Característica", "3", "—", "—", "—", "—"],
            ["5", "+3", "Ataque Adicional", "4", "2", "—", "—", "—"],
            ["6", "+3", "Aura de Protección", "4", "2", "—", "—", "—"],
            ["7", "+3", "Rasgo de Juramento Sagrado", "4", "3", "—", "—", "—"],
            ["8", "+3", "Mejora de Característica", "4", "3", "—", "—", "—"],
            ["9", "+4", "—", "4", "3", "2", "—", "—"],
            ["10", "+4", "Aura de Coraje", "4", "3", "2", "—", "—"],
            ["11", "+4", "Castigo Divino Mejorado", "4", "3", "3", "—", "—"],
            ["12", "+4", "Mejora de Característica", "4", "3", "3", "—", "—"],
            ["13", "+5", "—", "4", "3", "3", "1", "—"],
            ["14", "+5", "Toque Purificador", "4", "3", "3", "1", "—"],
            ["15", "+5", "Rasgo de Juramento Sagrado", "4", "3", "3", "2", "—"],
            ["16", "+5", "Mejora de Característica", "4", "3", "3", "2", "—"],
            ["17", "+6", "—", "4", "3", "3", "3", "1"],
            ["18", "+6", "Mejoras de Auras", "4", "3", "3", "3", "1"],
            ["19", "+6", "Mejora de Característica", "4", "3", "3", "3", "2"],
            ["20", "+6", "Rasgo de Juramento Sagrado", "4", "3", "3", "3", "2"],
        ]
    },
    "Pícaro": {
        "columnas": ["Nivel", "Bon. por competencia", "Ataque Furtivo", "Rasgos"],
        "filas": [
            ["1", "+2", "1d6", "Pericia, Ataque Furtivo, Jerga de Ladrones"],
            ["2", "+2", "1d6", "Acción Astuta"],
            ["3", "+2", "2d6", "Arquetipo de Pícaro"],
            ["4", "+2", "2d6", "Mejora de Característica"],
            ["5", "+3", "3d6", "Esquiva Asombrosa"],
            ["6", "+3", "3d6", "Pericia"],
            ["7", "+3", "4d6", "Evasión"],
            ["8", "+3", "4d6", "Mejora de Característica"],
            ["9", "+4", "5d6", "Rasgo de Arquetipo"],
            ["10", "+4", "5d6", "Mejora de Característica"],
            ["11", "+4", "6d6", "Talentos Fiables"],
            ["12", "+4", "6d6", "Mejora de Característica"],
            ["13", "+5", "7d6", "Rasgo de Arquetipo de Pícaro"],
            ["14", "+5", "7d6", "Sentir sin Ver"],
            ["15", "+5", "8d6", "Mente Escurridiza"],
            ["16", "+5", "8d6", "Mejora de Característica"],
            ["17", "+6", "9d6", "Rasgo de Arquetipo de Pícaro"],
            ["18", "+6", "9d6", "Elusivo"],
            ["19", "+6", "10d6", "Mejora de Característica"],
            ["20", "+6", "10d6", "Golpe de Suerte"],
        ]
    },
}


def inject_tables():
    path = "data/clases_razas.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    for item in data:
        name = item.get("nombre")
        if name in TABLE_DATA:
            item["tabla"] = TABLE_DATA[name]
            updated += 1
            print(f"  + {name}")

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nDone. {updated} classes updated.")


if __name__ == "__main__":
    inject_tables()
