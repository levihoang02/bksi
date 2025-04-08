import docker

client = docker.from_env()

SKELETON_DIR = "./skeleton"

def build_image_from_skeleton(image_tag: str):
    """Build Docker image từ thư mục skeleton"""
    try:
        print(f"🔨 Building image {image_tag}...")
        image, logs = client.images.build(path=SKELETON_DIR, tag=image_tag)
        for log in logs:
            print(log.get('stream', '').strip())
        return image
    except Exception as e:
        raise RuntimeError(f"Error building image: {str(e)}")


def create_and_run_container(image_tag: str, container_name: str, port: int = 8120):
    """Tạo và chạy container từ image"""
    try:
        container = client.containers.run(
            image_tag,
            name=container_name,
            detach=True,
            ports={f"{port}/tcp": port},
            network="bksi_app-network",
        )
        print(f"🚀 Container {container_name} started!")
        return container
    except Exception as e:
        raise RuntimeError(f"Error running container: {str(e)}")
    
def remove_container_from_id(id: str):
    try:
        c= client.containers.get(id)
        c.remove(force=True)
    except Exception as e:
        raise RuntimeError(f"Error running container: {str(e)}")
        