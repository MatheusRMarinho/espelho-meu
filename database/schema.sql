--tabela cliente
CREATE TABLE cliente (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL -- hash da senha
);

--tabela profissional
CREATE TABLE profissional (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    especialidade VARCHAR(100),
    tel VARCHAR(20)
);

--tabela servico
CREATE TABLE servico (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10, 2) NOT NULL,
    duracaoEmMinutos INT NOT NULL
);

-- tabela agendamento
CREATE TABLE agendamento (
    id SERIAL PRIMARY KEY,
    dataHora TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'Agendado',
    dataCriacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dataAlteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Chaves Estrangeiras
    cliente_id INT NOT NULL,
    profissional_id INT NOT NULL,
    servico_id INT NOT NULL,
    
    CONSTRAINT fk_cliente FOREIGN KEY (cliente_id) REFERENCES cliente(id) ON DELETE CASCADE,
    CONSTRAINT fk_profissional FOREIGN KEY (profissional_id) REFERENCES profissional(id) ON DELETE CASCADE,
    CONSTRAINT fk_servico FOREIGN KEY (servico_id) REFERENCES servico(id) ON DELETE CASCADE
);