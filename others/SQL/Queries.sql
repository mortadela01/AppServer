select * from tbl_deceased_video;

select * from tbl_user;	

insert into tbl_user(name, email, password) values ("example", "example@gmail.com", "1234");

select * from tbl_deceased_image;	
select * from tbl_relation;	

 -- Consultas VR

-- Obtener un id_user a partir de un número de código QR (qr_code)

SELECT id_user, visualization_status
FROM TBL_QR
WHERE qr_code = 111111111;

-- Obtener todos los datos de fallecidos pertenecientes a un id_user

SELECT d.*
FROM TBL_DECEASED d
JOIN TBL_USER_DECEASED ud ON d.id_deceased = ud.id_deceased
WHERE ud.id_user = 3;

-- Obtener las imágenes con su metadata correspondientes a un id_deceased, ordenadas por fecha (date_created)

SELECT img.*, imd.date_created, imd.coordinates
FROM TBL_DECEASED_IMAGE di
JOIN TBL_IMAGE img ON di.id_image = img.id_image
JOIN TBL_IMAGE_METADATA imd ON di.id_metadata = imd.id_metadata
WHERE di.id_deceased = 2
ORDER BY imd.date_created ASC;

-- Obtener los videos con su metadata correspondientes a un id_deceased, ordenados por fecha (date_created)

SELECT vid.*, vmd.date_created, vmd.coordinates
FROM TBL_DECEASED_VIDEO dv
JOIN TBL_VIDEO vid ON dv.id_video = vid.id_video
JOIN TBL_VIDEO_METADATA vmd ON dv.id_metadata = vmd.id_metadata
WHERE dv.id_deceased = 2
ORDER BY vmd.date_created ASC;

-- Obtener todas las relaciones de un fallecido y el tipo de relación, a través del id de fallecido (id_deceased)

SELECT 
    r.id_parent,           -- ID del familiar relacionado (padre, madre, etc.)
    rt.relationship       -- Tipo de relación (ej. padre, madre, hijo, etc.)
FROM TBL_RELATION r
JOIN TBL_RELATIONSHIP_TYPE rt ON r.relationship = rt.relationship
WHERE r.id_deceased = 2;

