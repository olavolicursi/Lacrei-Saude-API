#!/bin/bash
# Smoke Tests - Verificações básicas após deploy
# Uso: ./smoke-tests.sh <base-url>

set -e

BASE_URL=${1:-"http://localhost:8000"}
TIMEOUT=30

echo "🧪 Running smoke tests on: $BASE_URL"
echo "=========================================="

# Função auxiliar para fazer requests
check_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3
    
    echo -n "Testing $description... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$BASE_URL$endpoint" || echo "000")
    
    if [ "$response" == "$expected_status" ]; then
        echo "✅ OK ($response)"
        return 0
    else
        echo "❌ FAILED (expected $expected_status, got $response)"
        return 1
    fi
}

# Contador de falhas
FAILED=0

# Test 1: Health Check
check_endpoint "/api/v1/health/" "200" "Health Check Endpoint" || ((FAILED++))

# Test 2: API Root
check_endpoint "/api/v1/" "200" "API Root" || ((FAILED++))

# Test 3: Admin (deve redirecionar ou retornar 200)
check_endpoint "/admin/" "302" "Django Admin" || check_endpoint "/admin/" "200" "Django Admin" || ((FAILED++))

# Test 4: Static files (pode não existir em dev)
echo -n "Testing Static Files... "
response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$BASE_URL/static/" || echo "000")
if [ "$response" == "200" ] || [ "$response" == "404" ]; then
    echo "✅ OK ($response - expected in this environment)"
else
    echo "⚠️ WARNING ($response)"
fi

# Test 5: Performance - Response time
echo -n "Testing Response Time... "
start_time=$(date +%s%N)
curl -s -o /dev/null --max-time $TIMEOUT "$BASE_URL/api/v1/health/"
end_time=$(date +%s%N)
duration=$(( ($end_time - $start_time) / 1000000 ))

if [ $duration -lt 1000 ]; then
    echo "✅ OK (${duration}ms)"
else
    echo "⚠️ SLOW (${duration}ms - expected < 1000ms)"
fi

# Test 6: Database connectivity (via health endpoint)
echo -n "Testing Database Connection... "
db_check=$(curl -s "$BASE_URL/api/v1/health/" | grep -o '"database":"healthy"' || echo "")
if [ -n "$db_check" ]; then
    echo "✅ OK"
else
    echo "⚠️ Cannot verify (health endpoint may not have db status)"
fi

# Resumo
echo ""
echo "=========================================="
if [ $FAILED -eq 0 ]; then
    echo "✅ All smoke tests passed!"
    exit 0
else
    echo "❌ $FAILED test(s) failed!"
    exit 1
fi
