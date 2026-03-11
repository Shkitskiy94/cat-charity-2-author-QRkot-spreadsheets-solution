from typing import Optional
import httpx


class YandexDiskClient:
    """Простой клиент для Яндекс.Диск API"""

    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://cloud-api.yandex.net/v1/disk"
        self.headers = {"Authorization": f"OAuth {token}"}
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def create_excel_file(self, title: str) -> tuple[str, str]:
        """Получает ссылку для загрузки Excel файла"""
        # Создаём папку для отчётов
        await self._create_folder()

        file_path = f"disk:/QRKot Reports/{title}.xlsx"

        # Получаем ссылку для загрузки
        response = await self._client.get(
            f"{self.base_url}/resources/upload",
            headers=self.headers,
            params={"path": file_path, "overwrite": "true"}
        )
        response.raise_for_status()

        return response.json()["href"], file_path

    async def upload_file(self, upload_url: str, content: bytes):
        """Загружает файл по полученной ссылке"""
        response = await self._client.put(
            upload_url,
            content=content,
            headers={"Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
        )
        response.raise_for_status()

    async def publish_file(self, file_path: str) -> str:
        """Делает файл публичным и возвращает ссылку"""
        # Публикуем файл
        await self._client.put(
            f"{self.base_url}/resources/publish",
            headers=self.headers,
            params={"path": file_path}
        )

        # Получаем информацию о файле с публичной ссылкой
        response = await self._client.get(
            f"{self.base_url}/resources",
            headers=self.headers,
            params={"path": file_path}
        )
        response.raise_for_status()

        data = response.json()
        return data.get("public_url", f"https://disk.yandex.ru/client/disk/QRKot Reports/{file_path.split('/')[-1]}")

    async def _create_folder(self):
        """Создаёт папку для отчётов, если её нет"""
        try:
            await self._client.put(
                f"{self.base_url}/resources",
                headers=self.headers,
                params={"path": "disk:/QRKot Reports"}
            )
        except httpx.HTTPStatusError as e:
            # Папка уже существует (код 409) - игнорируем
            if e.response.status_code != 409:
                raise


async def get_yandex_client():
    """Dependency для получения клиента Яндекс.Диска"""
    from app.core.config import settings

    async with YandexDiskClient(settings.yandex_disk_token) as client:
        yield client