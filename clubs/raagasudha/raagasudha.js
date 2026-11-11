document.addEventListener("DOMContentLoaded", () => {

    const nav = document.querySelector('nav');
    const container = document.querySelector(".container");
    const menuToggle = document.querySelector(".menu-toggle");
    const menuOverlay = document.querySelector(".menu-overlay");
    const menuContent = document.querySelector(".menu-content");
    const menuPreviewImg = document.querySelector(".menu-preview-img");
    const menuLinks = document.querySelectorAll(".link a");

    let isOpen = false;
    let isAnimating = false;

    // navigation bar
    window.addEventListener('scroll', () => {
        if (window.scrollY > container.offsetTop) {
            nav.classList.add('active');
        } else {
            nav.classList.remove('active');
        }
    });

    // gallery
    const galleryImages = [
    document.getElementById('img1'),
    document.getElementById('img2'),
    document.getElementById('img3'),
    document.getElementById('img4'),
    document.getElementById('img5'),
    document.getElementById('img6'),
    document.getElementById('img7'),
    document.getElementById('img8'),
    document.getElementById('img9'),
    document.getElementById('img10')
    ];

    const windowDiv = document.querySelector('.window');

    const section = document.querySelector(".gallery");
    const sectionTop = section.offsetTop;
    const spreadStart = sectionTop+100;
    const maxSpread = 300; // stop motion after 300px

    window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;

    if (scrollY < spreadStart) {
        galleryImages.forEach(img => {
        img.style.transform = 'translate(0, 0) scale(1)';
        });
        windowDiv.style.transform = 'translate(0, 0)';
    } else {
        const rawScroll = scrollY - spreadStart;
        const scrollPast = Math.min(rawScroll, maxSpread);
        const scale = 0.5;

        galleryImages[0].style.transform = `translate(${scrollPast * -1.7}px, ${scrollPast * 2.5}px) scale(${scale})`;
        galleryImages[1].style.transform = `translate(${scrollPast * 1.7}px, ${scrollPast * 2.5}px) scale(${scale})`;
        galleryImages[2].style.transform = `translate(${scrollPast * 1.2}px, ${scrollPast * 2}px) scale(${scale})`;
        galleryImages[3].style.transform = `translate(${scrollPast * -1.8}px, ${scrollPast * 1.5}px) scale(${scale})`;
        galleryImages[4].style.transform = `translate(${scrollPast * -1.3}px, ${scrollPast * 2.1}px) scale(${scale})`;
        galleryImages[5].style.transform = `translate(${scrollPast * -0.6}px, ${scrollPast * 2.8}px) scale(${scale})`;
        galleryImages[6].style.transform = `translate(${scrollPast * 1.7}px, ${scrollPast * 1.7}px) scale(${scale})`;
        galleryImages[7].style.transform = `translate(${scrollPast * 0.8}px, ${scrollPast * 2.7}px) scale(${scale})`;
        galleryImages[8].style.transform = `translate(${scrollPast * -0.8}px, ${scrollPast * 1.6}px) scale(${scale})`;
        galleryImages[9].style.transform = `translate(${scrollPast * 0.9}px, ${scrollPast * 1.2}px) scale(${scale})`;
        windowDiv.style.transform = `translate(${scrollPast * -0.1}px, ${scrollPast * 2.27}px)`;
    }
    });



    // menu with gsap animations
    menuToggle.addEventListener("click", () => {
        if (!isOpen) openMenu();
        else closeMenu();
    });

    function cleanupPreviewImages() {
        const previewImages = menuPreviewImg.querySelectorAll("img");
        if (previewImages.length > 3) {
            for (let i = 0; i < previewImages.length - 3; i++) {
                menuPreviewImg.removeChild(previewImages[i]);
            }
        }
    }

    function resetPreviewImage() {
        menuPreviewImg.innerHTML = "";
        const defaultPreviewImg = document.createElement("img");
        defaultPreviewImg.src = "students_background.jpg";
        menuPreviewImg.appendChild(defaultPreviewImg);
    }

    function animateMenuToggle(isOpening) {
        const open = document.querySelector("p#menu-open");
        const close = document.querySelector("p#menu-close");

        gsap.to(isOpening ? open : close, {
            x: isOpening ? -5 : 5,
            y: isOpening ? -10 : 10,
            rotation: isOpening ? -5 : 5,
            opacity: 0,
            delay: 0.25,
            duration: 0.5,
            ease: "power2.out",
        });

        gsap.to(isOpening ? close : open, {
            x: 0,
            y: 0,
            rotation: 0,
            opacity: 1,
            delay: 0.5,
            duration: 0.5,
            ease: "power2.out",
        });
    }

    function openMenu() {
        if (isAnimating || isOpen) return;
        isAnimating = true;

        gsap.to(container, {
            rotation: 10,
            x: 300,
            y: 450,
            scale: 1.5,
            duration: 1.25,
            ease: "power4.inOut",
        });

        animateMenuToggle(true);

        gsap.to(menuContent, {
            rotation: 0,
            x: 0,
            y: 0,
            scale: 1,
            opacity: 1,
            duration: 1.25,
            ease: "power4.inOut",
        });

        gsap.to([".link a", ".social a"], {
            y: "0%",
            opacity: 1,
            duration: 1,
            delay: 0.75,
            stagger: 0.1,
            ease: "power3.out",
        });

        gsap.to(menuOverlay, {
            clipPath: "polygon(0% 0%, 100% 0%, 100% 175%, 0% 100%)",
            duration: 1.25,
            ease: "power4.inOut",
            onComplete: () => {
                isOpen = true;
                isAnimating = false;
            },
        });
    }

    function closeMenu() {
        if (isAnimating || !isOpen) return;
        isAnimating = true;

        gsap.to(container, {
            rotation: 0,
            x: 0,
            y: 0,
            scale: 1,
            duration: 1.25,
            ease: "power4.inOut",
        });

        animateMenuToggle(false);

        gsap.to(menuContent, {
            rotation: -15,
            x: -100,
            y: -100,
            scale: 1.5,
            opacity: 0.25,
            duration: 1.25,
            ease: "power4.inOut",
        });

        gsap.to(menuOverlay, {
            clipPath: "polygon(0% 0%, 100% 0%, 100% 0%, 0% 0%)",
            duration: 1.25,
            ease: "power4.inOut",
            onComplete: () => {
                isOpen = false;
                isAnimating = false;
                gsap.set([".link a", ".social a"], { y: "120%" });
                resetPreviewImage();
            },
        });
    }

    menuLinks.forEach((link) => {
        link.addEventListener("mouseover", () => {
            if (!isOpen || isAnimating) return;

            const imgSrc = link.getAttribute("data-img");
            if(!imgSrc) return;

            const previewImages = menuPreviewImg.querySelectorAll("img");
            if (
                previewImages.length > 0 &&
                previewImages[previewImages.length - 1].src.endsWith(imgSrc)
            )
                return;

            const newPreviewImg = document.createElement("img");
            newPreviewImg.src = imgSrc;
            newPreviewImg.style.opacity = "0";
            newPreviewImg.style.transform = "scale(1.25) rotate(10deg)";

            menuPreviewImg.appendChild(newPreviewImg);
            cleanupPreviewImages();

            gsap.to(newPreviewImg, {
                opacity: 1,
                scale: 1,
                rotation: 0,
                duration: 0.75,
                ease: "power2.out",
            });
        });
    });
});