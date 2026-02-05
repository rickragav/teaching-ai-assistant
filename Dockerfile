FROM agysacrdev.azurecr.io/official/almalinux-python:latest

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Set Python path so modules can be found
ENV PYTHONPATH=/app

# Upgrade SQLite3 to meet ChromaDB requirements (>= 3.35.0)
RUN yum install -y gcc make wget && \
    cd /tmp && \
    wget https://www.sqlite.org/2024/sqlite-autoconf-3450100.tar.gz && \
    tar xzf sqlite-autoconf-3450100.tar.gz && \
    cd sqlite-autoconf-3450100 && \
    ./configure --prefix=/usr/local && \
    make && \
    make install && \
    echo "/usr/local/lib" > /etc/ld.so.conf.d/sqlite3.conf && \
    ldconfig && \
    cd / && \
    rm -rf /tmp/sqlite-autoconf-3450100* && \
    yum clean all

# Set environment variable for SQLite3
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Download models at build time
RUN python3 src/voice_agent.py download-files

# Expose port
EXPOSE 8080

# Run the application
CMD ["python3", "src/voice_agent.py", "start"]