#!/bin/bash
# update_from_remote.sh
# Update local repository from remote (GitHub)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "원격 저장소에서 업데이트 가져오기"
echo "=========================================="

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ 오류: Git 저장소가 아닙니다."
    exit 1
fi

# Show current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "현재 브랜치: $CURRENT_BRANCH"
echo ""

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  경고: 커밋되지 않은 변경사항이 있습니다."
    echo ""
    echo "다음 중 선택하세요:"
    echo "1) 변경사항을 stash하고 업데이트"
    echo "2) 변경사항을 커밋하고 업데이트"
    echo "3) 취소"
    read -p "선택 (1/2/3): " choice
    
    case $choice in
        1)
            echo "변경사항을 stash합니다..."
            git stash
            STASHED=true
            ;;
        2)
            echo "변경사항을 커밋합니다..."
            git add -A
            git commit -m "Local changes before update"
            ;;
        3)
            echo "취소되었습니다."
            exit 0
            ;;
        *)
            echo "잘못된 선택입니다."
            exit 1
            ;;
    esac
fi

# Fetch latest changes from remote
echo ""
echo "원격 저장소에서 최신 변경사항 가져오는 중..."
git fetch origin

# Check if there are updates
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/$CURRENT_BRANCH 2>/dev/null || echo "")

if [ -z "$REMOTE" ]; then
    echo "❌ 오류: 원격 브랜치 '$CURRENT_BRANCH'를 찾을 수 없습니다."
    exit 1
fi

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✅ 이미 최신 상태입니다."
else
    echo ""
    echo "업데이트가 있습니다. 병합 중..."
    git pull origin $CURRENT_BRANCH
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ 업데이트 완료!"
        echo ""
        echo "최근 커밋:"
        git log --oneline -5
        
        # Restore stashed changes if any
        if [ "$STASHED" = true ]; then
            echo ""
            echo "Stash된 변경사항을 복원합니다..."
            git stash pop
        fi
    else
        echo ""
        echo "❌ 업데이트 중 충돌이 발생했습니다."
        echo "충돌을 해결한 후 다음 명령어를 실행하세요:"
        echo "  git add <충돌파일>"
        echo "  git commit -m 'Merge conflict resolved'"
        exit 1
    fi
fi

echo ""
echo "=========================================="

