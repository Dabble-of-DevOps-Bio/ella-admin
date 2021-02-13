--
-- Name: alleleassessment_classification; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.alleleassessment_classification AS ENUM (
    '1',
    '2',
    '3',
    '4',
    '5',
    'U',
    'DR'
);


ALTER TYPE public.alleleassessment_classification OWNER TO postgres;

--
-- Name: alleleinterpretation_workflow_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.alleleinterpretation_workflow_status AS ENUM (
    'Interpretation',
    'Review'
);


ALTER TYPE public.alleleinterpretation_workflow_status OWNER TO postgres;

--
-- Name: analysisinterpretation_workflow_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.analysisinterpretation_workflow_status AS ENUM (
    'Not ready',
    'Interpretation',
    'Review',
    'Medical review'
);


ALTER TYPE public.analysisinterpretation_workflow_status OWNER TO postgres;

--
-- Name: change_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.change_type AS ENUM (
    'SNP',
    'del',
    'ins',
    'indel'
);


ALTER TYPE public.change_type OWNER TO postgres;

--
-- Name: genotypesampledata_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.genotypesampledata_type AS ENUM (
    'Homozygous',
    'Heterozygous',
    'Reference',
    'No coverage'
);


ALTER TYPE public.genotypesampledata_type OWNER TO postgres;

--
-- Name: interpretation_endaction; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.interpretation_endaction AS ENUM (
    'Mark review',
    'Finalize'
);


ALTER TYPE public.interpretation_endaction OWNER TO postgres;

--
-- Name: interpretation_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.interpretation_status AS ENUM (
    'Not started',
    'Ongoing',
    'Done'
);


ALTER TYPE public.interpretation_status OWNER TO postgres;

--
-- Name: interpretationsnapshot_filtered; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.interpretationsnapshot_filtered AS ENUM (
    'FREQUENCY',
    'REGION',
    'POLYPYRIMIDINE',
    'GENE',
    'QUALITY',
    'CONSEQUENCE',
    'SEGREGATION',
    'INHERITANCEMODEL',
    'CLASSIFICATION'
);


ALTER TYPE public.interpretationsnapshot_filtered OWNER TO postgres;

--
-- Name: job_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.job_status AS ENUM (
    'SUBMITTED',
    'RUNNING',
    'ANNOTATED',
    'CANCELLED',
    'DONE',
    'FAILED (SUBMISSION)',
    'FAILED (ANNOTATION)',
    'FAILED (DEPOSIT)',
    'FAILED (PROCESSING)'
);


ALTER TYPE public.job_status OWNER TO postgres;

--
-- Name: mode; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.mode AS ENUM (
    'Analysis',
    'Variants',
    'Single variant'
);


ALTER TYPE public.mode OWNER TO postgres;

--
-- Name: sample_sex; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.sample_sex AS ENUM (
    'Male',
    'Female'
);


ALTER TYPE public.sample_sex OWNER TO postgres;

--
-- Name: sample_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.sample_type AS ENUM (
    'HTS',
    'Sanger'
);


ALTER TYPE public.sample_type OWNER TO postgres;

--
-- Name: transcript_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.transcript_type AS ENUM (
    'RefSeq',
    'Ensembl',
    'LRG'
);


ALTER TYPE public.transcript_type OWNER TO postgres;

--
-- Name: tsq_state; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tsq_state AS (
	search_query text,
	parentheses_stack integer,
	skip_for integer,
	current_token text,
	current_index integer,
	current_char text,
	previous_char text,
	tokens text[]
);


ALTER TYPE public.tsq_state OWNER TO postgres;

--
-- Name: _validate_json_schema_type(text, jsonb); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public._validate_json_schema_type(type text, data jsonb) RETURNS boolean
    LANGUAGE plpgsql IMMUTABLE
    AS $$
        BEGIN
        IF type = 'integer' THEN
            IF jsonb_typeof(data) != 'number' THEN
            RETURN false;
            END IF;
            IF trunc(data::text::numeric) != data::text::numeric THEN
            RETURN false;
            END IF;
        ELSE
            IF type != jsonb_typeof(data) THEN
            RETURN false;
            END IF;
        END IF;
        RETURN true;
        END;
        $$;


ALTER FUNCTION public._validate_json_schema_type(type text, data jsonb) OWNER TO postgres;

--
-- Name: annotation_schema_version(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.annotation_schema_version() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
            BEGIN
                NEW.schema_version = schema_version(NEW.annotations, 'annotation', false);
                RETURN NEW;
            END;
        $$;


ALTER FUNCTION public.annotation_schema_version() OWNER TO postgres;

--
-- Name: annotation_to_annotationshadow(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.annotation_to_annotationshadow() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            IF (TG_OP = 'INSERT') THEN
                PERFORM delete_annotationshadow(NEW.allele_id);
                PERFORM insert_annotationshadowtranscript(NEW.allele_id, NEW.annotations);
                PERFORM insert_annotationshadowfrequency(NEW.allele_id, NEW.annotations);
                RETURN NEW;
            ELSIF (TG_OP = 'UPDATE') THEN
                IF (
                    NEW.allele_id != OLD.allele_id OR
                    NEW.annotations != OLD.annotations OR
                    NEW.date_created != OLD.date_created
                ) THEN
                    RAISE EXCEPTION 'Update on one or more of the included columns for annotation table is disallowed';
                END IF;
                RETURN NEW;
            ELSIF (TG_OP = 'DELETE') THEN
                PERFORM delete_annotationshadow(allele_id);
                RETURN OLD;
            END IF;
        END;
    $$;


ALTER FUNCTION public.annotation_to_annotationshadow() OWNER TO postgres;

--
-- Name: array_nremove(anyarray, anyelement, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.array_nremove(anyarray, anyelement, integer) RETURNS anyarray
    LANGUAGE sql IMMUTABLE
    AS $_$
    WITH replaced_positions AS (
        SELECT UNNEST(
            CASE
            WHEN $2 IS NULL THEN
                '{}'::int[]
            WHEN $3 > 0 THEN
                (array_positions($1, $2))[1:$3]
            WHEN $3 < 0 THEN
                (array_positions($1, $2))[
                    (cardinality(array_positions($1, $2)) + $3 + 1):
                ]
            ELSE
                '{}'::int[]
            END
        ) AS position
    )
    SELECT COALESCE((
        SELECT array_agg(value)
        FROM unnest($1) WITH ORDINALITY AS t(value, index)
        WHERE index NOT IN (SELECT position FROM replaced_positions)
    ), $1[1:0]);
$_$;


ALTER FUNCTION public.array_nremove(anyarray, anyelement, integer) OWNER TO postgres;

--
-- Name: delete_annotationshadow(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.delete_annotationshadow(al_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
        BEGIN
            DELETE FROM annotationshadowtranscript WHERE allele_id = al_id;
            DELETE FROM annotationshadowfrequency WHERE allele_id = al_id;
        END;
    $$;


ALTER FUNCTION public.delete_annotationshadow(al_id integer) OWNER TO postgres;

--
-- Name: filterconfig_schema_version(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.filterconfig_schema_version() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
            BEGIN
                NEW.schema_version = schema_version(NEW.filterconfig, 'filterconfig', false);
                RETURN NEW;
            END;
        $$;


ALTER FUNCTION public.filterconfig_schema_version() OWNER TO postgres;

--
-- Name: insert_annotationshadowfrequency(integer, jsonb); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.insert_annotationshadowfrequency(allele_id integer, annotations jsonb) RETURNS void
    LANGUAGE plpgsql
    AS $$
        BEGIN
            INSERT INTO annotationshadowfrequency
                (
                    allele_id,
                    "GNOMAD_GENOMES.G",
"GNOMAD_GENOMES_num.G",
"GNOMAD_GENOMES.AFR",
"GNOMAD_GENOMES_num.AFR",
"GNOMAD_GENOMES.AMR",
"GNOMAD_GENOMES_num.AMR",
"GNOMAD_GENOMES.ASJ",
"GNOMAD_GENOMES_num.ASJ",
"GNOMAD_GENOMES.EAS",
"GNOMAD_GENOMES_num.EAS",
"GNOMAD_GENOMES.FIN",
"GNOMAD_GENOMES_num.FIN",
"GNOMAD_GENOMES.NFE",
"GNOMAD_GENOMES_num.NFE",
"GNOMAD_GENOMES.OTH",
"GNOMAD_GENOMES_num.OTH",
"GNOMAD_GENOMES.SAS",
"GNOMAD_GENOMES_num.SAS",
"GNOMAD_EXOMES.G",
"GNOMAD_EXOMES_num.G",
"GNOMAD_EXOMES.AFR",
"GNOMAD_EXOMES_num.AFR",
"GNOMAD_EXOMES.AMR",
"GNOMAD_EXOMES_num.AMR",
"GNOMAD_EXOMES.ASJ",
"GNOMAD_EXOMES_num.ASJ",
"GNOMAD_EXOMES.EAS",
"GNOMAD_EXOMES_num.EAS",
"GNOMAD_EXOMES.FIN",
"GNOMAD_EXOMES_num.FIN",
"GNOMAD_EXOMES.NFE",
"GNOMAD_EXOMES_num.NFE",
"GNOMAD_EXOMES.OTH",
"GNOMAD_EXOMES_num.OTH",
"GNOMAD_EXOMES.SAS",
"GNOMAD_EXOMES_num.SAS",
"inDB.OUSWES",
"inDB_num.OUSWES"
                )
                VALUES (
                    allele_id,
                    (annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'G')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'G')::integer,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'AFR')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'AFR')::integer,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'AMR')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'AMR')::integer,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'ASJ')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'ASJ')::integer,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'EAS')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'EAS')::integer,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'FIN')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'FIN')::integer,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'NFE')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'NFE')::integer,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'OTH')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'OTH')::integer,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'SAS')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'SAS')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'G')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'G')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'AFR')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'AFR')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'AMR')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'AMR')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'ASJ')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'ASJ')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'EAS')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'EAS')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'FIN')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'FIN')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'NFE')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'NFE')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'OTH')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'OTH')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'SAS')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'SAS')::integer,
(annotations->'frequencies'->'inDB'->'freq'->>'OUSWES')::float,
(annotations->'frequencies'->'inDB'->'num'->>'OUSWES')::integer
                );

        END;
    $$;


ALTER FUNCTION public.insert_annotationshadowfrequency(allele_id integer, annotations jsonb) OWNER TO postgres;

--
-- Name: insert_annotationshadowtranscript(integer, jsonb); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.insert_annotationshadowtranscript(allele_id integer, annotations jsonb) RETURNS void
    LANGUAGE plpgsql
    AS $$
        BEGIN
            INSERT INTO annotationshadowtranscript
                (
                    allele_id,
                    hgnc_id,
                    symbol,
                    transcript,
                    hgvsc,
                    protein,
                    hgvsp,
                    consequences,
                    exon_distance,
                    coding_region_distance
                )
                SELECT allele_id,
                    (a->>'hgnc_id')::integer,
                    a->>'symbol',
                    a->>'transcript',
                    a->>'HGVSc',
                    a->>'protein',
                    a->>'HGVSp',
                    ARRAY(SELECT jsonb_array_elements_text(a->'consequences')),
                    (a->>'exon_distance')::integer,
                    (a->>'coding_region_distance')::integer
                FROM jsonb_array_elements(annotations->'transcripts') as a;
        END;
    $$;


ALTER FUNCTION public.insert_annotationshadowtranscript(allele_id integer, annotations jsonb) OWNER TO postgres;

--
-- Name: insert_tmp_annotationshadowfrequency(integer, jsonb); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.insert_tmp_annotationshadowfrequency(allele_id integer, annotations jsonb) RETURNS void
    LANGUAGE plpgsql
    AS $$
        BEGIN
            INSERT INTO tmp_annotationshadowfrequency
                (
                    allele_id,
                    "GNOMAD_GENOMES.G",
"GNOMAD_GENOMES_num.G",
"GNOMAD_GENOMES.AFR",
"GNOMAD_GENOMES_num.AFR",
"GNOMAD_GENOMES.AMR",
"GNOMAD_GENOMES_num.AMR",
"GNOMAD_GENOMES.ASJ",
"GNOMAD_GENOMES_num.ASJ",
"GNOMAD_GENOMES.EAS",
"GNOMAD_GENOMES_num.EAS",
"GNOMAD_GENOMES.FIN",
"GNOMAD_GENOMES_num.FIN",
"GNOMAD_GENOMES.NFE",
"GNOMAD_GENOMES_num.NFE",
"GNOMAD_GENOMES.OTH",
"GNOMAD_GENOMES_num.OTH",
"GNOMAD_GENOMES.SAS",
"GNOMAD_GENOMES_num.SAS",
"GNOMAD_EXOMES.G",
"GNOMAD_EXOMES_num.G",
"GNOMAD_EXOMES.AFR",
"GNOMAD_EXOMES_num.AFR",
"GNOMAD_EXOMES.AMR",
"GNOMAD_EXOMES_num.AMR",
"GNOMAD_EXOMES.ASJ",
"GNOMAD_EXOMES_num.ASJ",
"GNOMAD_EXOMES.EAS",
"GNOMAD_EXOMES_num.EAS",
"GNOMAD_EXOMES.FIN",
"GNOMAD_EXOMES_num.FIN",
"GNOMAD_EXOMES.NFE",
"GNOMAD_EXOMES_num.NFE",
"GNOMAD_EXOMES.OTH",
"GNOMAD_EXOMES_num.OTH",
"GNOMAD_EXOMES.SAS",
"GNOMAD_EXOMES_num.SAS",
"inDB.OUSWES",
"inDB_num.OUSWES"
                )
                VALUES (
                    allele_id,
                    (annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'G')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'G')::integer,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'AFR')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'AFR')::integer,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'AMR')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'AMR')::integer,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'ASJ')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'ASJ')::integer,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'EAS')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'EAS')::integer,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'FIN')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'FIN')::integer,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'NFE')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'NFE')::integer,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'OTH')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'OTH')::integer,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'freq'->>'SAS')::float,
(annotations->'frequencies'->'GNOMAD_GENOMES'->'num'->>'SAS')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'G')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'G')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'AFR')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'AFR')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'AMR')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'AMR')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'ASJ')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'ASJ')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'EAS')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'EAS')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'FIN')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'FIN')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'NFE')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'NFE')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'OTH')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'OTH')::integer,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'freq'->>'SAS')::float,
(annotations->'frequencies'->'GNOMAD_EXOMES'->'num'->>'SAS')::integer,
(annotations->'frequencies'->'inDB'->'freq'->>'OUSWES')::float,
(annotations->'frequencies'->'inDB'->'num'->>'OUSWES')::integer
                );

        END;
    $$;


ALTER FUNCTION public.insert_tmp_annotationshadowfrequency(allele_id integer, annotations jsonb) OWNER TO postgres;

--
-- Name: insert_tmp_annotationshadowtranscript(integer, jsonb); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.insert_tmp_annotationshadowtranscript(allele_id integer, annotations jsonb) RETURNS void
    LANGUAGE plpgsql
    AS $$
        BEGIN
            INSERT INTO tmp_annotationshadowtranscript
                (
                    allele_id,
                    hgnc_id,
                    symbol,
                    transcript,
                    hgvsc,
                    protein,
                    hgvsp,
                    consequences,
                    exon_distance,
                    coding_region_distance
                )
                SELECT allele_id,
                    (a->>'hgnc_id')::integer,
                    a->>'symbol',
                    a->>'transcript',
                    a->>'HGVSc',
                    a->>'protein',
                    a->>'HGVSp',
                    ARRAY(SELECT jsonb_array_elements_text(a->'consequences')),
                    (a->>'exon_distance')::integer,
                    (a->>'coding_region_distance')::integer
                FROM jsonb_array_elements(annotations->'transcripts') as a;
        END;
    $$;


ALTER FUNCTION public.insert_tmp_annotationshadowtranscript(allele_id integer, annotations jsonb) OWNER TO postgres;

--
-- Name: schema_version(jsonb, text, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.schema_version(data jsonb, schema_name text, allow_null boolean DEFAULT true) RETURNS integer
    LANGUAGE plpgsql IMMUTABLE
    AS $$
        DECLARE
        available_schema_versions int[];
        x int;
        match int;
        BEGIN
            available_schema_versions = ARRAY(SELECT version FROM jsonschema WHERE name = schema_name ORDER BY version DESC);
            FOREACH x in ARRAY available_schema_versions LOOP
                IF validate_json_schema(schema, data) FROM jsonschema where version = x and name = schema_name THEN
                    RETURN x;
                END IF;
            END LOOP;
        IF allow_null IS FALSE THEN
            RAISE EXCEPTION  'schema_name=%, data=% ---- failed to validate against any of the existing schemas', schema_name, data USING ERRCODE='JSONV';
        END IF;
        RETURN NULL;
        END;
        $$;


ALTER FUNCTION public.schema_version(data jsonb, schema_name text, allow_null boolean) OWNER TO postgres;

--
-- Name: tsq_append_current_token(public.tsq_state); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.tsq_append_current_token(state public.tsq_state) RETURNS public.tsq_state
    LANGUAGE plpgsql IMMUTABLE
    AS $$
BEGIN
    IF state.current_token != '' THEN
        state.tokens := array_append(state.tokens, state.current_token);
        state.current_token := '';
    END IF;
    RETURN state;
END;
$$;


ALTER FUNCTION public.tsq_append_current_token(state public.tsq_state) OWNER TO postgres;

--
-- Name: tsq_process_tokens(regconfig, text[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.tsq_process_tokens(config regconfig, tokens text[]) RETURNS tsquery
    LANGUAGE plpgsql IMMUTABLE
    AS $$
DECLARE
    result_query text;
    previous_value text;
    value text;
BEGIN
    result_query := '';
    FOREACH value IN ARRAY tokens LOOP
        IF value = '"' THEN
            CONTINUE;
        END IF;

        IF left(value, 1) = '"' AND right(value, 1) = '"' THEN
            value := phraseto_tsquery(config, value);
        ELSIF value NOT IN ('(', ' | ', ')', '-') THEN
            value := quote_literal(value) || ':*';
        END IF;

        IF previous_value = '-' THEN
            IF value = '(' THEN
                value := '!' || value;
            ELSE
                value := '!(' || value || ')';
            END IF;
        END IF;

        SELECT
            CASE
                WHEN result_query = '' THEN value
                WHEN (
                    previous_value IN ('!(', '(', ' | ') OR
                    value IN (')', ' | ')
                ) THEN result_query || value
                ELSE result_query || ' & ' || value
            END
        INTO result_query;
        previous_value := value;
    END LOOP;

    RETURN to_tsquery(config, result_query);
END;
$$;


ALTER FUNCTION public.tsq_process_tokens(config regconfig, tokens text[]) OWNER TO postgres;

--
-- Name: tsq_tokenize(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.tsq_tokenize(search_query text) RETURNS text[]
    LANGUAGE plpgsql IMMUTABLE
    AS $$
DECLARE
    state tsq_state;
BEGIN
    SELECT
        search_query::text AS search_query,
        0::int AS parentheses_stack,
        0 AS skip_for,
        ''::text AS current_token,
        0 AS current_index,
        ''::text AS current_char,
        ''::text AS previous_char,
        '{}'::text[] AS tokens
    INTO state;

    state.search_query := lower(trim(
        regexp_replace(search_query, '""+', '""', 'g')
    ));

    FOR state.current_index IN (
        SELECT generate_series(1, length(state.search_query))
    ) LOOP
        state.current_char := substring(
            search_query FROM state.current_index FOR 1
        );

        IF state.skip_for > 0 THEN
            state.skip_for := state.skip_for - 1;
            CONTINUE;
        END IF;

        state := tsq_tokenize_character(state);
        state.previous_char := state.current_char;
    END LOOP;
    state := tsq_append_current_token(state);

    state.tokens := array_nremove(state.tokens, '(', -state.parentheses_stack);

    RETURN state.tokens;
END;
$$;


ALTER FUNCTION public.tsq_tokenize(search_query text) OWNER TO postgres;

--
-- Name: tsq_tokenize_character(public.tsq_state); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.tsq_tokenize_character(state public.tsq_state) RETURNS public.tsq_state
    LANGUAGE plpgsql IMMUTABLE
    AS $$
BEGIN
    IF state.current_char = '(' THEN
        state.tokens := array_append(state.tokens, '(');
        state.parentheses_stack := state.parentheses_stack + 1;
        state := tsq_append_current_token(state);
    ELSIF state.current_char = ')' THEN
        IF (state.parentheses_stack > 0 AND state.current_token != '') THEN
            state := tsq_append_current_token(state);
            state.tokens := array_append(state.tokens, ')');
            state.parentheses_stack := state.parentheses_stack - 1;
        END IF;
    ELSIF state.current_char = '"' THEN
        state.skip_for := position('"' IN substring(
            state.search_query FROM state.current_index + 1
        ));

        IF state.skip_for > 1 THEN
            state.tokens = array_append(
                state.tokens,
                substring(
                    state.search_query
                    FROM state.current_index FOR state.skip_for + 1
                )
            );
        ELSIF state.skip_for = 0 THEN
            state.current_token := state.current_token || state.current_char;
        END IF;
    ELSIF (
        state.current_char = '-' AND
        (state.current_index = 1 OR state.previous_char = ' ')
    ) THEN
        state.tokens := array_append(state.tokens, '-');
    ELSIF state.current_char = ' ' THEN
        state := tsq_append_current_token(state);
        IF substring(
            state.search_query FROM state.current_index FOR 4
        ) = ' or ' THEN
            state.skip_for := 2;

            -- remove duplicate OR tokens
            IF state.tokens[array_length(state.tokens, 1)] != ' | ' THEN
                state.tokens := array_append(state.tokens, ' | ');
            END IF;
        END IF;
    ELSE
        state.current_token = state.current_token || state.current_char;
    END IF;
    RETURN state;
END;
$$;


ALTER FUNCTION public.tsq_tokenize_character(state public.tsq_state) OWNER TO postgres;

--
-- Name: validate_json_schema(jsonb, jsonb, jsonb); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.validate_json_schema(schema jsonb, data jsonb, root_schema jsonb DEFAULT NULL::jsonb) RETURNS boolean
    LANGUAGE plpgsql IMMUTABLE
    AS $_$
        DECLARE
        prop text;
        item jsonb;
        path text[];
        types text[];
        pattern text;
        props text[];
        BEGIN
        IF root_schema IS NULL THEN
            root_schema = schema;
        END IF;

        IF schema ? 'type' THEN
            IF jsonb_typeof(schema->'type') = 'array' THEN
            types = ARRAY(SELECT jsonb_array_elements_text(schema->'type'));
            ELSE
            types = ARRAY[schema->>'type'];
            END IF;
            IF (SELECT NOT bool_or(_validate_json_schema_type(type, data)) FROM unnest(types) type) THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'properties' THEN
            FOR prop IN SELECT jsonb_object_keys(schema->'properties') LOOP
            IF data ? prop AND NOT validate_json_schema(schema->'properties'->prop, data->prop, root_schema) THEN
                RETURN false;
            END IF;
            END LOOP;
        END IF;

        IF schema ? 'required' AND jsonb_typeof(data) = 'object' THEN
            IF NOT ARRAY(SELECT jsonb_object_keys(data)) @>
                ARRAY(SELECT jsonb_array_elements_text(schema->'required')) THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'items' AND jsonb_typeof(data) = 'array' THEN
            IF jsonb_typeof(schema->'items') = 'object' THEN
            FOR item IN SELECT jsonb_array_elements(data) LOOP
                IF NOT validate_json_schema(schema->'items', item, root_schema) THEN
                RETURN false;
                END IF;
            END LOOP;
            ELSE
            IF NOT (
                SELECT bool_and(i > jsonb_array_length(schema->'items') OR validate_json_schema(schema->'items'->(i::int - 1), elem, root_schema))
                FROM jsonb_array_elements(data) WITH ORDINALITY AS t(elem, i)
            ) THEN
                RETURN false;
            END IF;
            END IF;
        END IF;

        IF jsonb_typeof(schema->'additionalItems') = 'boolean' and NOT (schema->'additionalItems')::text::boolean AND jsonb_typeof(schema->'items') = 'array' THEN
            IF jsonb_array_length(data) > jsonb_array_length(schema->'items') THEN
            RETURN false;
            END IF;
        END IF;

        IF jsonb_typeof(schema->'additionalItems') = 'object' THEN
            IF NOT (
                SELECT bool_and(validate_json_schema(schema->'additionalItems', elem, root_schema))
                FROM jsonb_array_elements(data) WITH ORDINALITY AS t(elem, i)
                WHERE i > jsonb_array_length(schema->'items')
            ) THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'minimum' AND jsonb_typeof(data) = 'number' THEN
            IF data::text::numeric < (schema->>'minimum')::numeric THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'maximum' AND jsonb_typeof(data) = 'number' THEN
            IF data::text::numeric > (schema->>'maximum')::numeric THEN
            RETURN false;
            END IF;
        END IF;

        IF COALESCE((schema->'exclusiveMinimum')::text::bool, FALSE) THEN
            IF data::text::numeric = (schema->>'minimum')::numeric THEN
            RETURN false;
            END IF;
        END IF;

        IF COALESCE((schema->'exclusiveMaximum')::text::bool, FALSE) THEN
            IF data::text::numeric = (schema->>'maximum')::numeric THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'anyOf' THEN
            IF NOT (SELECT bool_or(validate_json_schema(sub_schema, data, root_schema)) FROM jsonb_array_elements(schema->'anyOf') sub_schema) THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'allOf' THEN
            IF NOT (SELECT bool_and(validate_json_schema(sub_schema, data, root_schema)) FROM jsonb_array_elements(schema->'allOf') sub_schema) THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'oneOf' THEN
            IF 1 != (SELECT COUNT(*) FROM jsonb_array_elements(schema->'oneOf') sub_schema WHERE validate_json_schema(sub_schema, data, root_schema)) THEN
            RETURN false;
            END IF;
        END IF;

        IF COALESCE((schema->'uniqueItems')::text::boolean, false) THEN
            IF (SELECT COUNT(*) FROM jsonb_array_elements(data)) != (SELECT count(DISTINCT val) FROM jsonb_array_elements(data) val) THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'additionalProperties' AND jsonb_typeof(data) = 'object' THEN
            props := ARRAY(
            SELECT key
            FROM jsonb_object_keys(data) key
            WHERE key NOT IN (SELECT jsonb_object_keys(schema->'properties'))
                AND NOT EXISTS (SELECT * FROM jsonb_object_keys(schema->'patternProperties') pat WHERE key ~ pat)
            );
            IF jsonb_typeof(schema->'additionalProperties') = 'boolean' THEN
            IF NOT (schema->'additionalProperties')::text::boolean AND jsonb_typeof(data) = 'object' AND NOT props <@ ARRAY(SELECT jsonb_object_keys(schema->'properties')) THEN
                RETURN false;
            END IF;
            ELSEIF NOT (
            SELECT bool_and(validate_json_schema(schema->'additionalProperties', data->key, root_schema))
            FROM unnest(props) key
            ) THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? '$ref' THEN
            path := ARRAY(
            SELECT regexp_replace(regexp_replace(path_part, '~1', '/'), '~0', '~')
            FROM UNNEST(regexp_split_to_array(schema->>'$ref', '/')) path_part
            );
            -- ASSERT path[1] = '#', 'only refs anchored at the root are supported';
            IF NOT validate_json_schema(root_schema #> path[2:array_length(path, 1)], data, root_schema) THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'enum' THEN
            IF NOT EXISTS (SELECT * FROM jsonb_array_elements(schema->'enum') val WHERE val = data) THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'minLength' AND jsonb_typeof(data) = 'string' THEN
            IF char_length(data #>> '{}') < (schema->>'minLength')::numeric THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'maxLength' AND jsonb_typeof(data) = 'string' THEN
            IF char_length(data #>> '{}') > (schema->>'maxLength')::numeric THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'not' THEN
            IF validate_json_schema(schema->'not', data, root_schema) THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'maxProperties' AND jsonb_typeof(data) = 'object' THEN
            IF (SELECT count(*) FROM jsonb_object_keys(data)) > (schema->>'maxProperties')::numeric THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'minProperties' AND jsonb_typeof(data) = 'object' THEN
            IF (SELECT count(*) FROM jsonb_object_keys(data)) < (schema->>'minProperties')::numeric THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'maxItems' AND jsonb_typeof(data) = 'array' THEN
            IF (SELECT count(*) FROM jsonb_array_elements(data)) > (schema->>'maxItems')::numeric THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'minItems' AND jsonb_typeof(data) = 'array' THEN
            IF (SELECT count(*) FROM jsonb_array_elements(data)) < (schema->>'minItems')::numeric THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'dependencies' THEN
            FOR prop IN SELECT jsonb_object_keys(schema->'dependencies') LOOP
            IF data ? prop THEN
                IF jsonb_typeof(schema->'dependencies'->prop) = 'array' THEN
                IF NOT (SELECT bool_and(data ? dep) FROM jsonb_array_elements_text(schema->'dependencies'->prop) dep) THEN
                    RETURN false;
                END IF;
                ELSE
                IF NOT validate_json_schema(schema->'dependencies'->prop, data, root_schema) THEN
                    RETURN false;
                END IF;
                END IF;
            END IF;
            END LOOP;
        END IF;

        IF schema ? 'pattern' AND jsonb_typeof(data) = 'string' THEN
            IF (data #>> '{}') !~ (schema->>'pattern') THEN
            RETURN false;
            END IF;
        END IF;

        IF schema ? 'patternProperties' AND jsonb_typeof(data) = 'object' THEN
            FOR prop IN SELECT jsonb_object_keys(data) LOOP
            FOR pattern IN SELECT jsonb_object_keys(schema->'patternProperties') LOOP
                RAISE NOTICE 'prop %s, pattern %, schema %', prop, pattern, schema->'patternProperties'->pattern;
                IF prop ~ pattern AND NOT validate_json_schema(schema->'patternProperties'->pattern, data->prop, root_schema) THEN
                RETURN false;
                END IF;
            END LOOP;
            END LOOP;
        END IF;

        IF schema ? 'multipleOf' AND jsonb_typeof(data) = 'number' THEN
            IF data::text::numeric % (schema->>'multipleOf')::numeric != 0 THEN
            RETURN false;
            END IF;
        END IF;

        RETURN true;
        END;
        $_$;


ALTER FUNCTION public.validate_json_schema(schema jsonb, data jsonb, root_schema jsonb) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: allele; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.allele (
    id integer NOT NULL,
    genome_reference character varying NOT NULL,
    chromosome character varying NOT NULL,
    start_position integer NOT NULL,
    open_end_position integer NOT NULL,
    change_from character varying NOT NULL,
    change_to character varying NOT NULL,
    change_type public.change_type NOT NULL,
    vcf_pos integer NOT NULL,
    vcf_ref character varying NOT NULL,
    vcf_alt character varying NOT NULL
);


ALTER TABLE public.allele OWNER TO postgres;

--
-- Name: allele_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.allele_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.allele_id_seq OWNER TO postgres;

--
-- Name: allele_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.allele_id_seq OWNED BY public.allele.id;


--
-- Name: alleleassessment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alleleassessment (
    id integer NOT NULL,
    classification public.alleleassessment_classification NOT NULL,
    evaluation jsonb,
    user_id integer NOT NULL,
    date_created timestamp with time zone NOT NULL,
    date_superceeded timestamp with time zone,
    previous_assessment_id integer,
    allele_id integer NOT NULL,
    genepanel_name character varying NOT NULL,
    genepanel_version character varying NOT NULL,
    analysis_id integer,
    annotation_id integer,
    custom_annotation_id integer,
    usergroup_id integer
);


ALTER TABLE public.alleleassessment OWNER TO postgres;

--
-- Name: alleleassessment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.alleleassessment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.alleleassessment_id_seq OWNER TO postgres;

--
-- Name: alleleassessment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.alleleassessment_id_seq OWNED BY public.alleleassessment.id;


--
-- Name: alleleassessmentattachment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alleleassessmentattachment (
    alleleassessment_id integer,
    attachment_id integer
);


ALTER TABLE public.alleleassessmentattachment OWNER TO postgres;

--
-- Name: alleleassessmentreferenceassessment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alleleassessmentreferenceassessment (
    alleleassessment_id integer,
    referenceassessment_id integer
);


ALTER TABLE public.alleleassessmentreferenceassessment OWNER TO postgres;

--
-- Name: alleleinterpretation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alleleinterpretation (
    id integer NOT NULL,
    genepanel_name character varying NOT NULL,
    genepanel_version character varying NOT NULL,
    user_state jsonb,
    state jsonb,
    status public.interpretation_status NOT NULL,
    date_last_update timestamp with time zone NOT NULL,
    date_created timestamp with time zone NOT NULL,
    allele_id integer NOT NULL,
    user_id integer,
    finalized boolean,
    workflow_status public.alleleinterpretation_workflow_status NOT NULL
);


ALTER TABLE public.alleleinterpretation OWNER TO postgres;

--
-- Name: alleleinterpretation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.alleleinterpretation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.alleleinterpretation_id_seq OWNER TO postgres;

--
-- Name: alleleinterpretation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.alleleinterpretation_id_seq OWNED BY public.alleleinterpretation.id;


--
-- Name: alleleinterpretationsnapshot; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alleleinterpretationsnapshot (
    id integer NOT NULL,
    date_created timestamp with time zone NOT NULL,
    filtered public.interpretationsnapshot_filtered,
    alleleinterpretation_id integer NOT NULL,
    allele_id integer NOT NULL,
    annotation_id integer,
    customannotation_id integer,
    alleleassessment_id integer,
    allelereport_id integer
);


ALTER TABLE public.alleleinterpretationsnapshot OWNER TO postgres;

--
-- Name: alleleinterpretationsnapshot_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.alleleinterpretationsnapshot_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.alleleinterpretationsnapshot_id_seq OWNER TO postgres;

--
-- Name: alleleinterpretationsnapshot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.alleleinterpretationsnapshot_id_seq OWNED BY public.alleleinterpretationsnapshot.id;


--
-- Name: allelereport; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.allelereport (
    id integer NOT NULL,
    evaluation jsonb,
    user_id integer NOT NULL,
    date_created timestamp with time zone NOT NULL,
    date_superceeded timestamp with time zone,
    previous_report_id integer,
    allele_id integer NOT NULL,
    analysis_id integer,
    alleleassessment_id integer,
    usergroup_id integer
);


ALTER TABLE public.allelereport OWNER TO postgres;

--
-- Name: allelereport_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.allelereport_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.allelereport_id_seq OWNER TO postgres;

--
-- Name: allelereport_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.allelereport_id_seq OWNED BY public.allelereport.id;


--
-- Name: analysis; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.analysis (
    id integer NOT NULL,
    name character varying NOT NULL,
    genepanel_name character varying,
    genepanel_version character varying,
    warnings character varying,
    report character varying,
    date_deposited timestamp with time zone NOT NULL,
    properties jsonb,
    date_requested timestamp with time zone
);


ALTER TABLE public.analysis OWNER TO postgres;

--
-- Name: analysis_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.analysis_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.analysis_id_seq OWNER TO postgres;

--
-- Name: analysis_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.analysis_id_seq OWNED BY public.analysis.id;


--
-- Name: analysisinterpretation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.analysisinterpretation (
    id integer NOT NULL,
    genepanel_name character varying NOT NULL,
    genepanel_version character varying NOT NULL,
    user_state jsonb,
    state jsonb,
    status public.interpretation_status NOT NULL,
    date_last_update timestamp with time zone NOT NULL,
    date_created timestamp with time zone NOT NULL,
    analysis_id integer NOT NULL,
    user_id integer,
    finalized boolean,
    workflow_status public.analysisinterpretation_workflow_status NOT NULL
);


ALTER TABLE public.analysisinterpretation OWNER TO postgres;

--
-- Name: analysisinterpretation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.analysisinterpretation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.analysisinterpretation_id_seq OWNER TO postgres;

--
-- Name: analysisinterpretation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.analysisinterpretation_id_seq OWNED BY public.analysisinterpretation.id;


--
-- Name: analysisinterpretationsnapshot; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.analysisinterpretationsnapshot (
    id integer NOT NULL,
    date_created timestamp with time zone NOT NULL,
    filtered public.interpretationsnapshot_filtered,
    analysisinterpretation_id integer NOT NULL,
    allele_id integer NOT NULL,
    annotation_id integer,
    customannotation_id integer,
    alleleassessment_id integer,
    allelereport_id integer
);


ALTER TABLE public.analysisinterpretationsnapshot OWNER TO postgres;

--
-- Name: analysisinterpretationsnapshot_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.analysisinterpretationsnapshot_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.analysisinterpretationsnapshot_id_seq OWNER TO postgres;

--
-- Name: analysisinterpretationsnapshot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.analysisinterpretationsnapshot_id_seq OWNED BY public.analysisinterpretationsnapshot.id;


--
-- Name: annotation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.annotation (
    id integer NOT NULL,
    allele_id integer,
    annotations jsonb,
    previous_annotation_id integer,
    date_superceeded timestamp with time zone,
    date_created timestamp with time zone NOT NULL,
    schema_version integer NOT NULL
);


ALTER TABLE public.annotation OWNER TO postgres;

--
-- Name: annotation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.annotation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.annotation_id_seq OWNER TO postgres;

--
-- Name: annotation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.annotation_id_seq OWNED BY public.annotation.id;


--
-- Name: annotationjob; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.annotationjob (
    id integer NOT NULL,
    task_id character varying,
    status public.job_status NOT NULL,
    status_history jsonb,
    mode public.mode,
    data character varying,
    message character varying,
    user_id integer,
    date_submitted timestamp with time zone NOT NULL,
    date_last_update timestamp with time zone NOT NULL,
    genepanel_name character varying,
    genepanel_version character varying,
    properties jsonb,
    sample_id character varying
);


ALTER TABLE public.annotationjob OWNER TO postgres;

--
-- Name: annotationjob_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.annotationjob_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.annotationjob_id_seq OWNER TO postgres;

--
-- Name: annotationjob_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.annotationjob_id_seq OWNED BY public.annotationjob.id;


--
-- Name: annotationshadowfrequency; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.annotationshadowfrequency (
    id integer NOT NULL,
    allele_id integer,
    "GNOMAD_GENOMES.G" double precision,
    "GNOMAD_GENOMES_num.G" integer,
    "GNOMAD_GENOMES.AFR" double precision,
    "GNOMAD_GENOMES_num.AFR" integer,
    "GNOMAD_GENOMES.AMR" double precision,
    "GNOMAD_GENOMES_num.AMR" integer,
    "GNOMAD_GENOMES.ASJ" double precision,
    "GNOMAD_GENOMES_num.ASJ" integer,
    "GNOMAD_GENOMES.EAS" double precision,
    "GNOMAD_GENOMES_num.EAS" integer,
    "GNOMAD_GENOMES.FIN" double precision,
    "GNOMAD_GENOMES_num.FIN" integer,
    "GNOMAD_GENOMES.NFE" double precision,
    "GNOMAD_GENOMES_num.NFE" integer,
    "GNOMAD_GENOMES.OTH" double precision,
    "GNOMAD_GENOMES_num.OTH" integer,
    "GNOMAD_GENOMES.SAS" double precision,
    "GNOMAD_GENOMES_num.SAS" integer,
    "GNOMAD_EXOMES.G" double precision,
    "GNOMAD_EXOMES_num.G" integer,
    "GNOMAD_EXOMES.AFR" double precision,
    "GNOMAD_EXOMES_num.AFR" integer,
    "GNOMAD_EXOMES.AMR" double precision,
    "GNOMAD_EXOMES_num.AMR" integer,
    "GNOMAD_EXOMES.ASJ" double precision,
    "GNOMAD_EXOMES_num.ASJ" integer,
    "GNOMAD_EXOMES.EAS" double precision,
    "GNOMAD_EXOMES_num.EAS" integer,
    "GNOMAD_EXOMES.FIN" double precision,
    "GNOMAD_EXOMES_num.FIN" integer,
    "GNOMAD_EXOMES.NFE" double precision,
    "GNOMAD_EXOMES_num.NFE" integer,
    "GNOMAD_EXOMES.OTH" double precision,
    "GNOMAD_EXOMES_num.OTH" integer,
    "GNOMAD_EXOMES.SAS" double precision,
    "GNOMAD_EXOMES_num.SAS" integer,
    "inDB.OUSWES" double precision,
    "inDB_num.OUSWES" integer
);


ALTER TABLE public.annotationshadowfrequency OWNER TO postgres;

--
-- Name: annotationshadowtranscript; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.annotationshadowtranscript (
    id integer NOT NULL,
    allele_id integer,
    hgnc_id integer,
    symbol character varying,
    transcript character varying,
    hgvsc character varying,
    protein character varying,
    hgvsp character varying,
    consequences text[],
    exon_distance integer,
    coding_region_distance integer
);


ALTER TABLE public.annotationshadowtranscript OWNER TO postgres;

--
-- Name: attachment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attachment (
    id integer NOT NULL,
    sha256 character varying,
    filename character varying NOT NULL,
    size bigint,
    date_created timestamp with time zone NOT NULL,
    mimetype character varying,
    extension character varying,
    user_id integer NOT NULL
);


ALTER TABLE public.attachment OWNER TO postgres;

--
-- Name: attachment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.attachment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.attachment_id_seq OWNER TO postgres;

--
-- Name: attachment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.attachment_id_seq OWNED BY public.attachment.id;


--
-- Name: broadcast; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.broadcast (
    id integer NOT NULL,
    date_created timestamp with time zone NOT NULL,
    message character varying NOT NULL,
    active boolean NOT NULL
);


ALTER TABLE public.broadcast OWNER TO postgres;

--
-- Name: broadcast_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.broadcast_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.broadcast_id_seq OWNER TO postgres;

--
-- Name: broadcast_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.broadcast_id_seq OWNED BY public.broadcast.id;


--
-- Name: clilog; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clilog (
    id integer NOT NULL,
    "time" timestamp with time zone NOT NULL,
    "user" character varying NOT NULL,
    "group" character varying NOT NULL,
    groupcommand character varying NOT NULL,
    command character varying NOT NULL,
    reason character varying,
    output character varying NOT NULL
);


ALTER TABLE public.clilog OWNER TO postgres;

--
-- Name: clilog_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.clilog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.clilog_id_seq OWNER TO postgres;

--
-- Name: clilog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.clilog_id_seq OWNED BY public.clilog.id;


--
-- Name: customannotation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customannotation (
    id integer NOT NULL,
    annotations jsonb,
    allele_id integer,
    user_id integer,
    previous_annotation_id integer,
    date_superceeded timestamp with time zone,
    date_created timestamp with time zone NOT NULL
);


ALTER TABLE public.customannotation OWNER TO postgres;

--
-- Name: customannotation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customannotation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.customannotation_id_seq OWNER TO postgres;

--
-- Name: customannotation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customannotation_id_seq OWNED BY public.customannotation.id;


--
-- Name: filterconfig; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.filterconfig (
    id integer NOT NULL,
    name character varying NOT NULL,
    filterconfig jsonb NOT NULL,
    active boolean NOT NULL,
    date_superceeded timestamp with time zone,
    previous_filterconfig_id integer,
    requirements jsonb DEFAULT '[]'::jsonb NOT NULL,
    schema_version integer NOT NULL
);


ALTER TABLE public.filterconfig OWNER TO postgres;

--
-- Name: filterconfig_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.filterconfig_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.filterconfig_id_seq OWNER TO postgres;

--
-- Name: filterconfig_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.filterconfig_id_seq OWNED BY public.filterconfig.id;


--
-- Name: gene; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gene (
    hgnc_id integer NOT NULL,
    hgnc_symbol character varying NOT NULL,
    ensembl_gene_id character varying,
    omim_entry_id integer
);


ALTER TABLE public.gene OWNER TO postgres;

--
-- Name: gene_hgnc_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gene_hgnc_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gene_hgnc_id_seq OWNER TO postgres;

--
-- Name: gene_hgnc_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gene_hgnc_id_seq OWNED BY public.gene.hgnc_id;


--
-- Name: geneassessment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.geneassessment (
    id integer NOT NULL,
    evaluation jsonb,
    user_id integer NOT NULL,
    usergroup_id integer,
    date_created timestamp with time zone NOT NULL,
    genepanel_name character varying NOT NULL,
    genepanel_version character varying NOT NULL,
    date_superceeded timestamp with time zone,
    previous_assessment_id integer,
    gene_id integer NOT NULL,
    analysis_id integer
);


ALTER TABLE public.geneassessment OWNER TO postgres;

--
-- Name: geneassessment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.geneassessment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.geneassessment_id_seq OWNER TO postgres;

--
-- Name: geneassessment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.geneassessment_id_seq OWNED BY public.geneassessment.id;


--
-- Name: genepanel; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.genepanel (
    name character varying NOT NULL,
    version character varying NOT NULL,
    genome_reference character varying NOT NULL,
    official boolean NOT NULL,
    date_created timestamp with time zone NOT NULL,
    user_id integer
);


ALTER TABLE public.genepanel OWNER TO postgres;

--
-- Name: genepanel_phenotype; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.genepanel_phenotype (
    genepanel_name character varying NOT NULL,
    genepanel_version character varying NOT NULL,
    phenotype_id integer NOT NULL
);


ALTER TABLE public.genepanel_phenotype OWNER TO postgres;

--
-- Name: genepanel_transcript; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.genepanel_transcript (
    genepanel_name character varying NOT NULL,
    genepanel_version character varying NOT NULL,
    transcript_id integer NOT NULL
);


ALTER TABLE public.genepanel_transcript OWNER TO postgres;

--
-- Name: genotype; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.genotype (
    id integer NOT NULL,
    allele_id integer NOT NULL,
    secondallele_id integer,
    sample_id integer NOT NULL,
    variant_quality integer,
    filter_status character varying
);


ALTER TABLE public.genotype OWNER TO postgres;

--
-- Name: genotype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.genotype_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.genotype_id_seq OWNER TO postgres;

--
-- Name: genotype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.genotype_id_seq OWNED BY public.genotype.id;


--
-- Name: genotypesampledata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.genotypesampledata (
    id integer NOT NULL,
    genotype_id integer NOT NULL,
    secondallele boolean NOT NULL,
    multiallelic boolean NOT NULL,
    type public.genotypesampledata_type NOT NULL,
    sample_id integer NOT NULL,
    genotype_quality smallint,
    sequencing_depth smallint,
    genotype_likelihood integer[],
    allele_depth jsonb,
    allele_ratio double precision
);


ALTER TABLE public.genotypesampledata OWNER TO postgres;

--
-- Name: genotypesampledata_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.genotypesampledata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.genotypesampledata_id_seq OWNER TO postgres;

--
-- Name: genotypesampledata_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.genotypesampledata_id_seq OWNED BY public.genotypesampledata.id;


--
-- Name: interpretationlog; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interpretationlog (
    id integer NOT NULL,
    alleleinterpretation_id integer,
    analysisinterpretation_id integer,
    user_id integer,
    date_created timestamp with time zone NOT NULL,
    message character varying,
    priority integer,
    review_comment character varying,
    warning_cleared boolean,
    alleleassessment_id integer,
    allelereport_id integer
);


ALTER TABLE public.interpretationlog OWNER TO postgres;

--
-- Name: interpretationlog_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interpretationlog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.interpretationlog_id_seq OWNER TO postgres;

--
-- Name: interpretationlog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interpretationlog_id_seq OWNED BY public.interpretationlog.id;


--
-- Name: interpretationstatehistory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interpretationstatehistory (
    id integer NOT NULL,
    alleleinterpretation_id integer,
    analysisinterpretation_id integer,
    user_id integer NOT NULL,
    date_created timestamp with time zone NOT NULL,
    state jsonb NOT NULL
);


ALTER TABLE public.interpretationstatehistory OWNER TO postgres;

--
-- Name: interpretationstatehistory_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interpretationstatehistory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.interpretationstatehistory_id_seq OWNER TO postgres;

--
-- Name: interpretationstatehistory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interpretationstatehistory_id_seq OWNED BY public.interpretationstatehistory.id;


--
-- Name: jsonschema; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jsonschema (
    id integer NOT NULL,
    name character varying NOT NULL,
    version integer NOT NULL,
    schema jsonb NOT NULL
);


ALTER TABLE public.jsonschema OWNER TO postgres;

--
-- Name: jsonschema_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.jsonschema_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.jsonschema_id_seq OWNER TO postgres;

--
-- Name: jsonschema_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.jsonschema_id_seq OWNED BY public.jsonschema.id;


--
-- Name: phenotype; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.phenotype (
    id integer NOT NULL,
    gene_id integer NOT NULL,
    description character varying NOT NULL,
    inheritance character varying NOT NULL,
    omim_id integer
);


ALTER TABLE public.phenotype OWNER TO postgres;

--
-- Name: phenotype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.phenotype_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.phenotype_id_seq OWNER TO postgres;

--
-- Name: phenotype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.phenotype_id_seq OWNED BY public.phenotype.id;


--
-- Name: reference; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reference (
    id integer NOT NULL,
    authors character varying,
    title character varying,
    journal character varying,
    abstract character varying,
    year character varying,
    pubmed_id integer,
    published boolean NOT NULL,
    attachment_id integer,
    search tsvector
);


ALTER TABLE public.reference OWNER TO postgres;

--
-- Name: reference_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reference_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reference_id_seq OWNER TO postgres;

--
-- Name: reference_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reference_id_seq OWNED BY public.reference.id;


--
-- Name: referenceassessment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.referenceassessment (
    id integer NOT NULL,
    reference_id integer NOT NULL,
    evaluation jsonb,
    user_id integer NOT NULL,
    date_created timestamp with time zone NOT NULL,
    date_superceeded timestamp with time zone,
    genepanel_name character varying NOT NULL,
    genepanel_version character varying NOT NULL,
    allele_id integer NOT NULL,
    previous_assessment_id integer,
    analysis_id integer,
    usergroup_id integer
);


ALTER TABLE public.referenceassessment OWNER TO postgres;

--
-- Name: referenceassessment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.referenceassessment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.referenceassessment_id_seq OWNER TO postgres;

--
-- Name: referenceassessment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.referenceassessment_id_seq OWNED BY public.referenceassessment.id;


--
-- Name: resourcelog; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.resourcelog (
    id integer NOT NULL,
    remote_addr inet NOT NULL,
    "time" timestamp with time zone NOT NULL,
    duration integer NOT NULL,
    usersession_id integer,
    method character varying NOT NULL,
    resource character varying NOT NULL,
    query character varying NOT NULL,
    response character varying,
    response_size integer NOT NULL,
    payload character varying,
    payload_size integer NOT NULL,
    statuscode integer NOT NULL
);


ALTER TABLE public.resourcelog OWNER TO postgres;

--
-- Name: resourcelog_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.resourcelog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.resourcelog_id_seq OWNER TO postgres;

--
-- Name: resourcelog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.resourcelog_id_seq OWNED BY public.resourcelog.id;


--
-- Name: sample; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sample (
    id integer NOT NULL,
    identifier character varying NOT NULL,
    analysis_id integer NOT NULL,
    sample_type public.sample_type NOT NULL,
    date_deposited timestamp with time zone NOT NULL,
    affected boolean NOT NULL,
    family_id character varying,
    father_id integer,
    mother_id integer,
    sibling_id integer,
    proband boolean NOT NULL,
    sex public.sample_sex
);


ALTER TABLE public.sample OWNER TO postgres;

--
-- Name: sample_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sample_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sample_id_seq OWNER TO postgres;

--
-- Name: sample_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sample_id_seq OWNED BY public.sample.id;


--
-- Name: tmp_annotationshadowfrequency_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tmp_annotationshadowfrequency_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tmp_annotationshadowfrequency_id_seq OWNER TO postgres;

--
-- Name: tmp_annotationshadowfrequency_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tmp_annotationshadowfrequency_id_seq OWNED BY public.annotationshadowfrequency.id;


--
-- Name: tmp_annotationshadowtranscript_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tmp_annotationshadowtranscript_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tmp_annotationshadowtranscript_id_seq OWNER TO postgres;

--
-- Name: tmp_annotationshadowtranscript_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tmp_annotationshadowtranscript_id_seq OWNED BY public.annotationshadowtranscript.id;


--
-- Name: transcript; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transcript (
    id integer NOT NULL,
    gene_id integer NOT NULL,
    transcript_name character varying NOT NULL,
    type public.transcript_type NOT NULL,
    corresponding_refseq character varying,
    corresponding_ensembl character varying,
    corresponding_lrg character varying,
    genome_reference character varying NOT NULL,
    chromosome character varying NOT NULL,
    tx_start integer NOT NULL,
    tx_end integer NOT NULL,
    strand character varying(1) NOT NULL,
    cds_start integer NOT NULL,
    cds_end integer NOT NULL,
    exon_starts integer[] NOT NULL,
    exon_ends integer[] NOT NULL
);


ALTER TABLE public.transcript OWNER TO postgres;

--
-- Name: transcript_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transcript_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.transcript_id_seq OWNER TO postgres;

--
-- Name: transcript_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transcript_id_seq OWNED BY public.transcript.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE IF NOT EXISTS public."user" (
    id integer NOT NULL,
    username character varying NOT NULL,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    group_id integer NOT NULL,
    password character varying NOT NULL,
    password_expiry timestamp with time zone NOT NULL,
    active boolean NOT NULL,
    incorrect_logins integer NOT NULL,
    config jsonb,
    email character varying
);


ALTER TABLE public."user" OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE IF NOT EXISTS public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_id_seq OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: usergroup; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usergroup (
    id integer NOT NULL,
    name character varying NOT NULL,
    config jsonb,
    default_import_genepanel_name character varying,
    default_import_genepanel_version character varying
);


ALTER TABLE public.usergroup OWNER TO postgres;

--
-- Name: usergroup_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usergroup_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.usergroup_id_seq OWNER TO postgres;

--
-- Name: usergroup_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usergroup_id_seq OWNED BY public.usergroup.id;


--
-- Name: usergroupfilterconfig; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usergroupfilterconfig (
    id integer NOT NULL,
    usergroup_id integer NOT NULL,
    filterconfig_id integer NOT NULL,
    "order" integer NOT NULL
);


ALTER TABLE public.usergroupfilterconfig OWNER TO postgres;

--
-- Name: usergroupfilterconfig_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usergroupfilterconfig_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.usergroupfilterconfig_id_seq OWNER TO postgres;

--
-- Name: usergroupfilterconfig_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usergroupfilterconfig_id_seq OWNED BY public.usergroupfilterconfig.id;


--
-- Name: usergroupgenepanel; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usergroupgenepanel (
    usergroup_id integer,
    genepanel_name character varying NOT NULL,
    genepanel_version character varying NOT NULL
);


ALTER TABLE public.usergroupgenepanel OWNER TO postgres;

--
-- Name: useroldpassword; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.useroldpassword (
    id integer NOT NULL,
    user_id integer,
    password character varying NOT NULL,
    expired timestamp with time zone NOT NULL
);


ALTER TABLE public.useroldpassword OWNER TO postgres;

--
-- Name: useroldpassword_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.useroldpassword_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.useroldpassword_id_seq OWNER TO postgres;

--
-- Name: useroldpassword_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.useroldpassword_id_seq OWNED BY public.useroldpassword.id;


--
-- Name: usersession; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usersession (
    id integer NOT NULL,
    user_id integer,
    token character varying NOT NULL,
    issued timestamp with time zone NOT NULL,
    lastactivity timestamp with time zone NOT NULL,
    expires timestamp with time zone NOT NULL,
    logged_out timestamp with time zone
);


ALTER TABLE public.usersession OWNER TO postgres;

--
-- Name: usersession_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usersession_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.usersession_id_seq OWNER TO postgres;

--
-- Name: usersession_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usersession_id_seq OWNED BY public.usersession.id;


--
-- Name: allele id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allele ALTER COLUMN id SET DEFAULT nextval('public.allele_id_seq'::regclass);


--
-- Name: alleleassessment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleassessment ALTER COLUMN id SET DEFAULT nextval('public.alleleassessment_id_seq'::regclass);


--
-- Name: alleleinterpretation id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleinterpretation ALTER COLUMN id SET DEFAULT nextval('public.alleleinterpretation_id_seq'::regclass);


--
-- Name: alleleinterpretationsnapshot id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleinterpretationsnapshot ALTER COLUMN id SET DEFAULT nextval('public.alleleinterpretationsnapshot_id_seq'::regclass);


--
-- Name: allelereport id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allelereport ALTER COLUMN id SET DEFAULT nextval('public.allelereport_id_seq'::regclass);


--
-- Name: analysis id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysis ALTER COLUMN id SET DEFAULT nextval('public.analysis_id_seq'::regclass);


--
-- Name: analysisinterpretation id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisinterpretation ALTER COLUMN id SET DEFAULT nextval('public.analysisinterpretation_id_seq'::regclass);


--
-- Name: analysisinterpretationsnapshot id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisinterpretationsnapshot ALTER COLUMN id SET DEFAULT nextval('public.analysisinterpretationsnapshot_id_seq'::regclass);


--
-- Name: annotation id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotation ALTER COLUMN id SET DEFAULT nextval('public.annotation_id_seq'::regclass);


--
-- Name: annotationjob id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotationjob ALTER COLUMN id SET DEFAULT nextval('public.annotationjob_id_seq'::regclass);


--
-- Name: annotationshadowfrequency id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotationshadowfrequency ALTER COLUMN id SET DEFAULT nextval('public.tmp_annotationshadowfrequency_id_seq'::regclass);


--
-- Name: annotationshadowtranscript id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotationshadowtranscript ALTER COLUMN id SET DEFAULT nextval('public.tmp_annotationshadowtranscript_id_seq'::regclass);


--
-- Name: attachment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attachment ALTER COLUMN id SET DEFAULT nextval('public.attachment_id_seq'::regclass);


--
-- Name: broadcast id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.broadcast ALTER COLUMN id SET DEFAULT nextval('public.broadcast_id_seq'::regclass);


--
-- Name: clilog id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clilog ALTER COLUMN id SET DEFAULT nextval('public.clilog_id_seq'::regclass);


--
-- Name: customannotation id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customannotation ALTER COLUMN id SET DEFAULT nextval('public.customannotation_id_seq'::regclass);


--
-- Name: filterconfig id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.filterconfig ALTER COLUMN id SET DEFAULT nextval('public.filterconfig_id_seq'::regclass);


--
-- Name: gene hgnc_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gene ALTER COLUMN hgnc_id SET DEFAULT nextval('public.gene_hgnc_id_seq'::regclass);


--
-- Name: geneassessment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.geneassessment ALTER COLUMN id SET DEFAULT nextval('public.geneassessment_id_seq'::regclass);


--
-- Name: genotype id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genotype ALTER COLUMN id SET DEFAULT nextval('public.genotype_id_seq'::regclass);


--
-- Name: genotypesampledata id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genotypesampledata ALTER COLUMN id SET DEFAULT nextval('public.genotypesampledata_id_seq'::regclass);


--
-- Name: interpretationlog id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interpretationlog ALTER COLUMN id SET DEFAULT nextval('public.interpretationlog_id_seq'::regclass);


--
-- Name: interpretationstatehistory id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interpretationstatehistory ALTER COLUMN id SET DEFAULT nextval('public.interpretationstatehistory_id_seq'::regclass);


--
-- Name: jsonschema id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jsonschema ALTER COLUMN id SET DEFAULT nextval('public.jsonschema_id_seq'::regclass);


--
-- Name: phenotype id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype ALTER COLUMN id SET DEFAULT nextval('public.phenotype_id_seq'::regclass);


--
-- Name: reference id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reference ALTER COLUMN id SET DEFAULT nextval('public.reference_id_seq'::regclass);


--
-- Name: referenceassessment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referenceassessment ALTER COLUMN id SET DEFAULT nextval('public.referenceassessment_id_seq'::regclass);


--
-- Name: resourcelog id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resourcelog ALTER COLUMN id SET DEFAULT nextval('public.resourcelog_id_seq'::regclass);


--
-- Name: sample id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sample ALTER COLUMN id SET DEFAULT nextval('public.sample_id_seq'::regclass);


--
-- Name: transcript id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transcript ALTER COLUMN id SET DEFAULT nextval('public.transcript_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Name: usergroup id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usergroup ALTER COLUMN id SET DEFAULT nextval('public.usergroup_id_seq'::regclass);


--
-- Name: usergroupfilterconfig id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usergroupfilterconfig ALTER COLUMN id SET DEFAULT nextval('public.usergroupfilterconfig_id_seq'::regclass);


--
-- Name: useroldpassword id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.useroldpassword ALTER COLUMN id SET DEFAULT nextval('public.useroldpassword_id_seq'::regclass);


--
-- Name: usersession id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usersession ALTER COLUMN id SET DEFAULT nextval('public.usersession_id_seq'::regclass);


--
-- Name: allele_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.allele_id_seq', 24, true);


--
-- Name: alleleassessment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.alleleassessment_id_seq', 6, true);


--
-- Name: alleleinterpretation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.alleleinterpretation_id_seq', 1, false);


--
-- Name: alleleinterpretationsnapshot_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.alleleinterpretationsnapshot_id_seq', 1, false);


--
-- Name: allelereport_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.allelereport_id_seq', 6, true);


--
-- Name: analysis_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.analysis_id_seq', 7, true);


--
-- Name: analysisinterpretation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.analysisinterpretation_id_seq', 7, true);


--
-- Name: analysisinterpretationsnapshot_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.analysisinterpretationsnapshot_id_seq', 1, false);


--
-- Name: annotation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.annotation_id_seq', 24, true);


--
-- Name: annotationjob_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.annotationjob_id_seq', 1, false);


--
-- Name: attachment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.attachment_id_seq', 1, false);


--
-- Name: broadcast_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.broadcast_id_seq', 1, false);


--
-- Name: clilog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.clilog_id_seq', 15, true);


--
-- Name: customannotation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.customannotation_id_seq', 1, false);


--
-- Name: filterconfig_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.filterconfig_id_seq', 3, true);


--
-- Name: gene_hgnc_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gene_hgnc_id_seq', 1, false);


--
-- Name: geneassessment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.geneassessment_id_seq', 1, false);


--
-- Name: genotype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.genotype_id_seq', 36, true);


--
-- Name: genotypesampledata_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.genotypesampledata_id_seq', 36, true);


--
-- Name: interpretationlog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.interpretationlog_id_seq', 13, true);


--
-- Name: interpretationstatehistory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.interpretationstatehistory_id_seq', 7, true);


--
-- Name: jsonschema_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.jsonschema_id_seq', 10, true);


--
-- Name: phenotype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.phenotype_id_seq', 5186, true);


--
-- Name: reference_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reference_id_seq', 1, false);


--
-- Name: referenceassessment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.referenceassessment_id_seq', 1, false);


--
-- Name: resourcelog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.resourcelog_id_seq', 102, true);


--
-- Name: sample_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sample_id_seq', 7, true);


--
-- Name: tmp_annotationshadowfrequency_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tmp_annotationshadowfrequency_id_seq', 24, true);


--
-- Name: tmp_annotationshadowtranscript_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tmp_annotationshadowtranscript_id_seq', 160, true);


--
-- Name: transcript_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.transcript_id_seq', 3603, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_id_seq', 8, true);


--
-- Name: usergroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usergroup_id_seq', 3, true);


--
-- Name: usergroupfilterconfig_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usergroupfilterconfig_id_seq', 6, true);


--
-- Name: useroldpassword_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.useroldpassword_id_seq', 2, true);


--
-- Name: usersession_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usersession_id_seq', 1, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: allele pk_allele; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allele
    ADD CONSTRAINT pk_allele PRIMARY KEY (id);


--
-- Name: alleleassessment pk_alleleassessment; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleassessment
    ADD CONSTRAINT pk_alleleassessment PRIMARY KEY (id);


--
-- Name: alleleinterpretation pk_alleleinterpretation; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleinterpretation
    ADD CONSTRAINT pk_alleleinterpretation PRIMARY KEY (id);


--
-- Name: alleleinterpretationsnapshot pk_alleleinterpretationsnapshot; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleinterpretationsnapshot
    ADD CONSTRAINT pk_alleleinterpretationsnapshot PRIMARY KEY (id);


--
-- Name: allelereport pk_allelereport; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allelereport
    ADD CONSTRAINT pk_allelereport PRIMARY KEY (id);


--
-- Name: analysis pk_analysis; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysis
    ADD CONSTRAINT pk_analysis PRIMARY KEY (id);


--
-- Name: analysisinterpretation pk_analysisinterpretation; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisinterpretation
    ADD CONSTRAINT pk_analysisinterpretation PRIMARY KEY (id);


--
-- Name: analysisinterpretationsnapshot pk_analysisinterpretationsnapshot; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisinterpretationsnapshot
    ADD CONSTRAINT pk_analysisinterpretationsnapshot PRIMARY KEY (id);


--
-- Name: annotation pk_annotation; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotation
    ADD CONSTRAINT pk_annotation PRIMARY KEY (id);


--
-- Name: annotationjob pk_annotationjob; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotationjob
    ADD CONSTRAINT pk_annotationjob PRIMARY KEY (id);


--
-- Name: annotationshadowfrequency pk_annotationshadowfrequency; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotationshadowfrequency
    ADD CONSTRAINT pk_annotationshadowfrequency PRIMARY KEY (id);


--
-- Name: annotationshadowtranscript pk_annotationshadowtranscript; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotationshadowtranscript
    ADD CONSTRAINT pk_annotationshadowtranscript PRIMARY KEY (id);


--
-- Name: attachment pk_attachment; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attachment
    ADD CONSTRAINT pk_attachment PRIMARY KEY (id);


--
-- Name: broadcast pk_broadcast; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.broadcast
    ADD CONSTRAINT pk_broadcast PRIMARY KEY (id);


--
-- Name: clilog pk_clilog; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clilog
    ADD CONSTRAINT pk_clilog PRIMARY KEY (id);


--
-- Name: customannotation pk_customannotation; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customannotation
    ADD CONSTRAINT pk_customannotation PRIMARY KEY (id);


--
-- Name: filterconfig pk_filterconfig; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.filterconfig
    ADD CONSTRAINT pk_filterconfig PRIMARY KEY (id);


--
-- Name: gene pk_gene; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gene
    ADD CONSTRAINT pk_gene PRIMARY KEY (hgnc_id);


--
-- Name: geneassessment pk_geneassessment; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.geneassessment
    ADD CONSTRAINT pk_geneassessment PRIMARY KEY (id);


--
-- Name: genepanel pk_genepanel; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genepanel
    ADD CONSTRAINT pk_genepanel PRIMARY KEY (name, version);


--
-- Name: genotype pk_genotype; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genotype
    ADD CONSTRAINT pk_genotype PRIMARY KEY (id);


--
-- Name: genotypesampledata pk_genotypesampledata; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genotypesampledata
    ADD CONSTRAINT pk_genotypesampledata PRIMARY KEY (id);


--
-- Name: interpretationlog pk_interpretationlog; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interpretationlog
    ADD CONSTRAINT pk_interpretationlog PRIMARY KEY (id);


--
-- Name: interpretationstatehistory pk_interpretationstatehistory; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interpretationstatehistory
    ADD CONSTRAINT pk_interpretationstatehistory PRIMARY KEY (id);


--
-- Name: jsonschema pk_jsonschema; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jsonschema
    ADD CONSTRAINT pk_jsonschema PRIMARY KEY (id);


--
-- Name: phenotype pk_phenotype; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype
    ADD CONSTRAINT pk_phenotype PRIMARY KEY (id);


--
-- Name: reference pk_reference; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reference
    ADD CONSTRAINT pk_reference PRIMARY KEY (id);


--
-- Name: referenceassessment pk_referenceassessment; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referenceassessment
    ADD CONSTRAINT pk_referenceassessment PRIMARY KEY (id);


--
-- Name: resourcelog pk_resourcelog; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resourcelog
    ADD CONSTRAINT pk_resourcelog PRIMARY KEY (id);


--
-- Name: sample pk_sample; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sample
    ADD CONSTRAINT pk_sample PRIMARY KEY (id);


--
-- Name: transcript pk_transcript; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transcript
    ADD CONSTRAINT pk_transcript PRIMARY KEY (id);


--
-- Name: user pk_user; Type: CONSTRAINT; Schema: public; Owner: postgres
--



--
-- Name: usergroup pk_usergroup; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usergroup
    ADD CONSTRAINT pk_usergroup PRIMARY KEY (id);


--
-- Name: usergroupfilterconfig pk_usergroupfilterconfig; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usergroupfilterconfig
    ADD CONSTRAINT pk_usergroupfilterconfig PRIMARY KEY (id);


--
-- Name: useroldpassword pk_useroldpassword; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.useroldpassword
    ADD CONSTRAINT pk_useroldpassword PRIMARY KEY (id);


--
-- Name: usersession pk_usersession; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usersession
    ADD CONSTRAINT pk_usersession PRIMARY KEY (id);


--
-- Name: allele ucAllele; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allele
    ADD CONSTRAINT "ucAllele" UNIQUE (chromosome, start_position, open_end_position, change_from, change_to, change_type, vcf_pos, vcf_ref, vcf_alt);


--
-- Name: alleleinterpretationsnapshot uq_alleleinterpretationsnapshot_alleleinterpretation_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleinterpretationsnapshot
    ADD CONSTRAINT uq_alleleinterpretationsnapshot_alleleinterpretation_id UNIQUE (alleleinterpretation_id, allele_id);


--
-- Name: analysis uq_analysis_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysis
    ADD CONSTRAINT uq_analysis_name UNIQUE (name);


--
-- Name: analysisinterpretationsnapshot uq_analysisinterpretationsnapshot_analysisinterpretation_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisinterpretationsnapshot
    ADD CONSTRAINT uq_analysisinterpretationsnapshot_analysisinterpretation_id UNIQUE (analysisinterpretation_id, allele_id);


--
-- Name: gene uq_gene_ensembl_gene_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gene
    ADD CONSTRAINT uq_gene_ensembl_gene_id UNIQUE (ensembl_gene_id);


--
-- Name: phenotype uq_phenotype_gene_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype
    ADD CONSTRAINT uq_phenotype_gene_id UNIQUE (gene_id, description, inheritance);


--
-- Name: reference uq_reference_pubmed_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reference
    ADD CONSTRAINT uq_reference_pubmed_id UNIQUE (pubmed_id);


--
-- Name: transcript uq_transcript_transcript_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transcript
    ADD CONSTRAINT uq_transcript_transcript_name UNIQUE (transcript_name);


--
-- Name: usergroup uq_usergroup_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usergroup
    ADD CONSTRAINT uq_usergroup_name UNIQUE (name);


--
-- Name: usersession uq_usersession_token; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usersession
    ADD CONSTRAINT uq_usersession_token UNIQUE (token);


--
-- Name: ix_alleleinterpretation_alleleid_ongoing_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_alleleinterpretation_alleleid_ongoing_unique ON public.alleleinterpretation USING btree (allele_id) WHERE (status = ANY (ARRAY['Ongoing'::public.interpretation_status, 'Not started'::public.interpretation_status]));


--
-- Name: ix_alleleloci; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_alleleloci ON public.allele USING btree (chromosome, start_position, open_end_position);


--
-- Name: ix_allelereport_alleleid_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_allelereport_alleleid_unique ON public.allelereport USING btree (allele_id) WHERE (date_superceeded IS NULL);


--
-- Name: ix_analysisinterpretation_analysisid_ongoing_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_analysisinterpretation_analysisid_ongoing_unique ON public.analysisinterpretation USING btree (analysis_id) WHERE (status = ANY (ARRAY['Ongoing'::public.interpretation_status, 'Not started'::public.interpretation_status]));


--
-- Name: ix_annotation_allele_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_annotation_allele_id ON public.annotation USING btree (allele_id);


--
-- Name: ix_annotation_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_annotation_unique ON public.annotation USING btree (allele_id) WHERE (date_superceeded IS NULL);


--
-- Name: ix_annotationshadowfrequency_allele_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_annotationshadowfrequency_allele_id ON public.annotationshadowfrequency USING btree (allele_id);


--
-- Name: ix_annotationshadowtranscript_allele_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_annotationshadowtranscript_allele_id ON public.annotationshadowtranscript USING btree (allele_id);


--
-- Name: ix_annotationshadowtranscript_hgnc_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_annotationshadowtranscript_hgnc_id ON public.annotationshadowtranscript USING btree (hgnc_id);


--
-- Name: ix_annotationshadowtranscript_hgvsc; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_annotationshadowtranscript_hgvsc ON public.annotationshadowtranscript USING btree (lower((hgvsc)::text));


--
-- Name: ix_annotationshadowtranscript_symbol; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_annotationshadowtranscript_symbol ON public.annotationshadowtranscript USING btree (symbol);


--
-- Name: ix_annotationshadowtranscript_transcript; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_annotationshadowtranscript_transcript ON public.annotationshadowtranscript USING btree (transcript);


--
-- Name: ix_assessment_alleleid_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_assessment_alleleid_unique ON public.alleleassessment USING btree (allele_id) WHERE (date_superceeded IS NULL);


--
-- Name: ix_customannotation_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_customannotation_unique ON public.customannotation USING btree (allele_id) WHERE (date_superceeded IS NULL);


--
-- Name: ix_gene_hgnc_symbol; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_gene_hgnc_symbol ON public.gene USING btree (lower((hgnc_symbol)::text) text_pattern_ops);


--
-- Name: ix_geneassessment_geneid_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_geneassessment_geneid_unique ON public.geneassessment USING btree (gene_id) WHERE (date_superceeded IS NULL);


--
-- Name: ix_genotype_sample_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_genotype_sample_id ON public.genotype USING btree (sample_id);


--
-- Name: ix_genotypesampledata_genotype_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_genotypesampledata_genotype_id ON public.genotypesampledata USING btree (genotype_id);


--
-- Name: ix_genotypesampledata_sample_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_genotypesampledata_sample_id ON public.genotypesampledata USING btree (sample_id);


--
-- Name: ix_jsonschema_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_jsonschema_unique ON public.jsonschema USING btree (name, version);


--
-- Name: ix_pubmedid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_pubmedid ON public.reference USING btree (pubmed_id);


--
-- Name: ix_reference_search; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reference_search ON public.reference USING gin (search);


--
-- Name: ix_referenceassessment_alleleid_referenceid_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_referenceassessment_alleleid_referenceid_unique ON public.referenceassessment USING btree (allele_id, reference_id) WHERE (date_superceeded IS NULL);


--
-- Name: ix_resourcelog_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resourcelog_time ON public.resourcelog USING btree ("time");


--
-- Name: ix_sampleidentifier; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sampleidentifier ON public.sample USING btree (identifier);


--
-- Name: uq_filterconfig_name_active_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_filterconfig_name_active_unique ON public.filterconfig USING btree (name) WHERE (active IS TRUE);


--
-- Name: uq_usergroupfilterconfig_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_usergroupfilterconfig_unique ON public.usergroupfilterconfig USING btree (usergroup_id, filterconfig_id);


--
-- Name: annotation annotation_schema_version; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER annotation_schema_version BEFORE INSERT OR UPDATE ON public.annotation FOR EACH ROW EXECUTE FUNCTION public.annotation_schema_version();


--
-- Name: annotation annotation_to_annotationshadow; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER annotation_to_annotationshadow BEFORE INSERT OR DELETE OR UPDATE ON public.annotation FOR EACH ROW EXECUTE FUNCTION public.annotation_to_annotationshadow();


--
-- Name: filterconfig filterconfig_schema_version; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER filterconfig_schema_version BEFORE INSERT OR UPDATE ON public.filterconfig FOR EACH ROW EXECUTE FUNCTION public.filterconfig_schema_version();


--
-- Name: alleleassessment fk_alleleassessment_allele_id_allele; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleassessment
    ADD CONSTRAINT fk_alleleassessment_allele_id_allele FOREIGN KEY (allele_id) REFERENCES public.allele(id);


--
-- Name: alleleassessment fk_alleleassessment_analysis_id_analysis; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleassessment
    ADD CONSTRAINT fk_alleleassessment_analysis_id_analysis FOREIGN KEY (analysis_id) REFERENCES public.analysis(id) ON DELETE SET NULL;


--
-- Name: alleleassessment fk_alleleassessment_annotation_id_annotation; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleassessment
    ADD CONSTRAINT fk_alleleassessment_annotation_id_annotation FOREIGN KEY (annotation_id) REFERENCES public.annotation(id);


--
-- Name: alleleassessment fk_alleleassessment_custom_annotation_id_customannotation; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleassessment
    ADD CONSTRAINT fk_alleleassessment_custom_annotation_id_customannotation FOREIGN KEY (custom_annotation_id) REFERENCES public.customannotation(id);


--
-- Name: alleleassessment fk_alleleassessment_genepanel_name_genepanel; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleassessment
    ADD CONSTRAINT fk_alleleassessment_genepanel_name_genepanel FOREIGN KEY (genepanel_name, genepanel_version) REFERENCES public.genepanel(name, version);


--
-- Name: alleleassessment fk_alleleassessment_previous_assessment_id_alleleassessment; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleassessment
    ADD CONSTRAINT fk_alleleassessment_previous_assessment_id_alleleassessment FOREIGN KEY (previous_assessment_id) REFERENCES public.alleleassessment(id);


--
-- Name: alleleassessment fk_alleleassessment_user_id_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleassessment
    ADD CONSTRAINT fk_alleleassessment_user_id_user FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: alleleassessment fk_alleleassessment_usergroup_id_usergroup; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleassessment
    ADD CONSTRAINT fk_alleleassessment_usergroup_id_usergroup FOREIGN KEY (usergroup_id) REFERENCES public.usergroup(id);


--
-- Name: alleleassessmentattachment fk_alleleassessmentattachment_alleleassessment_id_alleleassessm; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleassessmentattachment
    ADD CONSTRAINT fk_alleleassessmentattachment_alleleassessment_id_alleleassessm FOREIGN KEY (alleleassessment_id) REFERENCES public.alleleassessment(id);


--
-- Name: alleleassessmentattachment fk_alleleassessmentattachment_attachment_id_attachment; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleassessmentattachment
    ADD CONSTRAINT fk_alleleassessmentattachment_attachment_id_attachment FOREIGN KEY (attachment_id) REFERENCES public.attachment(id);


--
-- Name: alleleassessmentreferenceassessment fk_alleleassessmentreferenceassessment_alleleassessment_id_alle; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleassessmentreferenceassessment
    ADD CONSTRAINT fk_alleleassessmentreferenceassessment_alleleassessment_id_alle FOREIGN KEY (alleleassessment_id) REFERENCES public.alleleassessment(id);


--
-- Name: alleleassessmentreferenceassessment fk_alleleassessmentreferenceassessment_referenceassessment_id_r; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleassessmentreferenceassessment
    ADD CONSTRAINT fk_alleleassessmentreferenceassessment_referenceassessment_id_r FOREIGN KEY (referenceassessment_id) REFERENCES public.referenceassessment(id);


--
-- Name: alleleinterpretation fk_alleleinterpretation_allele_id_allele; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleinterpretation
    ADD CONSTRAINT fk_alleleinterpretation_allele_id_allele FOREIGN KEY (allele_id) REFERENCES public.allele(id);


--
-- Name: alleleinterpretation fk_alleleinterpretation_genepanel_name_genepanel; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleinterpretation
    ADD CONSTRAINT fk_alleleinterpretation_genepanel_name_genepanel FOREIGN KEY (genepanel_name, genepanel_version) REFERENCES public.genepanel(name, version);


--
-- Name: alleleinterpretation fk_alleleinterpretation_user_id_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleinterpretation
    ADD CONSTRAINT fk_alleleinterpretation_user_id_user FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: alleleinterpretationsnapshot fk_alleleinterpretationsnapshot_allele_id_allele; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleinterpretationsnapshot
    ADD CONSTRAINT fk_alleleinterpretationsnapshot_allele_id_allele FOREIGN KEY (allele_id) REFERENCES public.allele(id);


--
-- Name: alleleinterpretationsnapshot fk_alleleinterpretationsnapshot_alleleassessment_id_alleleasses; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleinterpretationsnapshot
    ADD CONSTRAINT fk_alleleinterpretationsnapshot_alleleassessment_id_alleleasses FOREIGN KEY (alleleassessment_id) REFERENCES public.alleleassessment(id);


--
-- Name: alleleinterpretationsnapshot fk_alleleinterpretationsnapshot_alleleinterpretation_id_allelei; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleinterpretationsnapshot
    ADD CONSTRAINT fk_alleleinterpretationsnapshot_alleleinterpretation_id_allelei FOREIGN KEY (alleleinterpretation_id) REFERENCES public.alleleinterpretation(id) ON DELETE CASCADE;


--
-- Name: alleleinterpretationsnapshot fk_alleleinterpretationsnapshot_allelereport_id_allelereport; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleinterpretationsnapshot
    ADD CONSTRAINT fk_alleleinterpretationsnapshot_allelereport_id_allelereport FOREIGN KEY (allelereport_id) REFERENCES public.allelereport(id);


--
-- Name: alleleinterpretationsnapshot fk_alleleinterpretationsnapshot_annotation_id_annotation; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleinterpretationsnapshot
    ADD CONSTRAINT fk_alleleinterpretationsnapshot_annotation_id_annotation FOREIGN KEY (annotation_id) REFERENCES public.annotation(id);


--
-- Name: alleleinterpretationsnapshot fk_alleleinterpretationsnapshot_customannotation_id_customannot; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alleleinterpretationsnapshot
    ADD CONSTRAINT fk_alleleinterpretationsnapshot_customannotation_id_customannot FOREIGN KEY (customannotation_id) REFERENCES public.customannotation(id);


--
-- Name: allelereport fk_allelereport_allele_id_allele; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allelereport
    ADD CONSTRAINT fk_allelereport_allele_id_allele FOREIGN KEY (allele_id) REFERENCES public.allele(id);


--
-- Name: allelereport fk_allelereport_alleleassessment_id_alleleassessment; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allelereport
    ADD CONSTRAINT fk_allelereport_alleleassessment_id_alleleassessment FOREIGN KEY (alleleassessment_id) REFERENCES public.alleleassessment(id);


--
-- Name: allelereport fk_allelereport_analysis_id_analysis; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allelereport
    ADD CONSTRAINT fk_allelereport_analysis_id_analysis FOREIGN KEY (analysis_id) REFERENCES public.analysis(id) ON DELETE SET NULL;


--
-- Name: allelereport fk_allelereport_previous_report_id_allelereport; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allelereport
    ADD CONSTRAINT fk_allelereport_previous_report_id_allelereport FOREIGN KEY (previous_report_id) REFERENCES public.allelereport(id);


--
-- Name: allelereport fk_allelereport_user_id_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allelereport
    ADD CONSTRAINT fk_allelereport_user_id_user FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: allelereport fk_allelereport_usergroup_id_usergroup; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allelereport
    ADD CONSTRAINT fk_allelereport_usergroup_id_usergroup FOREIGN KEY (usergroup_id) REFERENCES public.usergroup(id);


--
-- Name: analysis fk_analysis_genepanel_name_genepanel; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysis
    ADD CONSTRAINT fk_analysis_genepanel_name_genepanel FOREIGN KEY (genepanel_name, genepanel_version) REFERENCES public.genepanel(name, version);


--
-- Name: analysisinterpretation fk_analysisinterpretation_analysis_id_analysis; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisinterpretation
    ADD CONSTRAINT fk_analysisinterpretation_analysis_id_analysis FOREIGN KEY (analysis_id) REFERENCES public.analysis(id) ON DELETE CASCADE;


--
-- Name: analysisinterpretation fk_analysisinterpretation_genepanel_name_genepanel; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisinterpretation
    ADD CONSTRAINT fk_analysisinterpretation_genepanel_name_genepanel FOREIGN KEY (genepanel_name, genepanel_version) REFERENCES public.genepanel(name, version);


--
-- Name: analysisinterpretation fk_analysisinterpretation_user_id_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisinterpretation
    ADD CONSTRAINT fk_analysisinterpretation_user_id_user FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: analysisinterpretationsnapshot fk_analysisinterpretationsnapshot_allele_id_allele; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisinterpretationsnapshot
    ADD CONSTRAINT fk_analysisinterpretationsnapshot_allele_id_allele FOREIGN KEY (allele_id) REFERENCES public.allele(id);


--
-- Name: analysisinterpretationsnapshot fk_analysisinterpretationsnapshot_alleleassessment_id_alleleass; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisinterpretationsnapshot
    ADD CONSTRAINT fk_analysisinterpretationsnapshot_alleleassessment_id_alleleass FOREIGN KEY (alleleassessment_id) REFERENCES public.alleleassessment(id);


--
-- Name: analysisinterpretationsnapshot fk_analysisinterpretationsnapshot_allelereport_id_allelereport; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisinterpretationsnapshot
    ADD CONSTRAINT fk_analysisinterpretationsnapshot_allelereport_id_allelereport FOREIGN KEY (allelereport_id) REFERENCES public.allelereport(id);


--
-- Name: analysisinterpretationsnapshot fk_analysisinterpretationsnapshot_analysisinterpretation_id_ana; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisinterpretationsnapshot
    ADD CONSTRAINT fk_analysisinterpretationsnapshot_analysisinterpretation_id_ana FOREIGN KEY (analysisinterpretation_id) REFERENCES public.analysisinterpretation(id) ON DELETE CASCADE;


--
-- Name: analysisinterpretationsnapshot fk_analysisinterpretationsnapshot_annotation_id_annotation; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisinterpretationsnapshot
    ADD CONSTRAINT fk_analysisinterpretationsnapshot_annotation_id_annotation FOREIGN KEY (annotation_id) REFERENCES public.annotation(id);


--
-- Name: analysisinterpretationsnapshot fk_analysisinterpretationsnapshot_customannotation_id_customann; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisinterpretationsnapshot
    ADD CONSTRAINT fk_analysisinterpretationsnapshot_customannotation_id_customann FOREIGN KEY (customannotation_id) REFERENCES public.customannotation(id);


--
-- Name: annotation fk_annotation_allele_id_allele; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotation
    ADD CONSTRAINT fk_annotation_allele_id_allele FOREIGN KEY (allele_id) REFERENCES public.allele(id);


--
-- Name: annotation fk_annotation_previous_annotation_id_annotation; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotation
    ADD CONSTRAINT fk_annotation_previous_annotation_id_annotation FOREIGN KEY (previous_annotation_id) REFERENCES public.annotation(id);


--
-- Name: annotationjob fk_annotationjob_genepanel_name_genepanel; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotationjob
    ADD CONSTRAINT fk_annotationjob_genepanel_name_genepanel FOREIGN KEY (genepanel_name, genepanel_version) REFERENCES public.genepanel(name, version);


--
-- Name: annotationjob fk_annotationjob_user_id_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotationjob
    ADD CONSTRAINT fk_annotationjob_user_id_user FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: annotationshadowfrequency fk_annotationshadowfrequency_allele_id_allele; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotationshadowfrequency
    ADD CONSTRAINT fk_annotationshadowfrequency_allele_id_allele FOREIGN KEY (allele_id) REFERENCES public.allele(id);


--
-- Name: annotationshadowtranscript fk_annotationshadowtranscript_allele_id_allele; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotationshadowtranscript
    ADD CONSTRAINT fk_annotationshadowtranscript_allele_id_allele FOREIGN KEY (allele_id) REFERENCES public.allele(id);


--
-- Name: attachment fk_attachment_user_id_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attachment
    ADD CONSTRAINT fk_attachment_user_id_user FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: customannotation fk_customannotation_allele_id_allele; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customannotation
    ADD CONSTRAINT fk_customannotation_allele_id_allele FOREIGN KEY (allele_id) REFERENCES public.allele(id);


--
-- Name: customannotation fk_customannotation_previous_annotation_id_customannotation; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customannotation
    ADD CONSTRAINT fk_customannotation_previous_annotation_id_customannotation FOREIGN KEY (previous_annotation_id) REFERENCES public.customannotation(id);


--
-- Name: customannotation fk_customannotation_user_id_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customannotation
    ADD CONSTRAINT fk_customannotation_user_id_user FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: filterconfig fk_filterconfig_previous_filterconfig_filterconfig; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.filterconfig
    ADD CONSTRAINT fk_filterconfig_previous_filterconfig_filterconfig FOREIGN KEY (previous_filterconfig_id) REFERENCES public.filterconfig(id);


--
-- Name: geneassessment fk_geneassessment_analysis_id_analysis; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.geneassessment
    ADD CONSTRAINT fk_geneassessment_analysis_id_analysis FOREIGN KEY (analysis_id) REFERENCES public.analysis(id) ON DELETE SET NULL;


--
-- Name: geneassessment fk_geneassessment_gene_id_gene; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.geneassessment
    ADD CONSTRAINT fk_geneassessment_gene_id_gene FOREIGN KEY (gene_id) REFERENCES public.gene(hgnc_id);


--
-- Name: geneassessment fk_geneassessment_previous_assessment_id_geneassessment; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.geneassessment
    ADD CONSTRAINT fk_geneassessment_previous_assessment_id_geneassessment FOREIGN KEY (previous_assessment_id) REFERENCES public.geneassessment(id);


--
-- Name: geneassessment fk_geneassessment_user_id_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.geneassessment
    ADD CONSTRAINT fk_geneassessment_user_id_user FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: geneassessment fk_geneassessment_usergroup_id_usergroup; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.geneassessment
    ADD CONSTRAINT fk_geneassessment_usergroup_id_usergroup FOREIGN KEY (usergroup_id) REFERENCES public.usergroup(id);


--
-- Name: genepanel_phenotype fk_genepanel_phenotype_genepanel_name_genepanel; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genepanel_phenotype
    ADD CONSTRAINT fk_genepanel_phenotype_genepanel_name_genepanel FOREIGN KEY (genepanel_name, genepanel_version) REFERENCES public.genepanel(name, version) ON DELETE CASCADE;


--
-- Name: genepanel_phenotype fk_genepanel_phenotype_phenotype_id_phenotype; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genepanel_phenotype
    ADD CONSTRAINT fk_genepanel_phenotype_phenotype_id_phenotype FOREIGN KEY (phenotype_id) REFERENCES public.phenotype(id);


--
-- Name: genepanel_transcript fk_genepanel_transcript_genepanel_name_genepanel; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genepanel_transcript
    ADD CONSTRAINT fk_genepanel_transcript_genepanel_name_genepanel FOREIGN KEY (genepanel_name, genepanel_version) REFERENCES public.genepanel(name, version) ON DELETE CASCADE;


--
-- Name: genepanel_transcript fk_genepanel_transcript_transcript_id_transcript; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genepanel_transcript
    ADD CONSTRAINT fk_genepanel_transcript_transcript_id_transcript FOREIGN KEY (transcript_id) REFERENCES public.transcript(id);


--
-- Name: genepanel fk_genepanel_user_id_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genepanel
    ADD CONSTRAINT fk_genepanel_user_id_user FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: genotype fk_genotype_allele_id_allele; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genotype
    ADD CONSTRAINT fk_genotype_allele_id_allele FOREIGN KEY (allele_id) REFERENCES public.allele(id);


--
-- Name: genotype fk_genotype_sample_id_sample; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genotype
    ADD CONSTRAINT fk_genotype_sample_id_sample FOREIGN KEY (sample_id) REFERENCES public.sample(id) ON DELETE CASCADE;


--
-- Name: genotype fk_genotype_secondallele_id_allele; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genotype
    ADD CONSTRAINT fk_genotype_secondallele_id_allele FOREIGN KEY (secondallele_id) REFERENCES public.allele(id);


--
-- Name: genotypesampledata fk_genotypesampledata_genotype_id_genotype; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genotypesampledata
    ADD CONSTRAINT fk_genotypesampledata_genotype_id_genotype FOREIGN KEY (genotype_id) REFERENCES public.genotype(id) ON DELETE CASCADE;


--
-- Name: genotypesampledata fk_genotypesampledata_sample_id_sample; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genotypesampledata
    ADD CONSTRAINT fk_genotypesampledata_sample_id_sample FOREIGN KEY (sample_id) REFERENCES public.sample(id) ON DELETE CASCADE;


--
-- Name: interpretationlog fk_interpretationlog_alleleassessment_id_alleleassessment; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interpretationlog
    ADD CONSTRAINT fk_interpretationlog_alleleassessment_id_alleleassessment FOREIGN KEY (alleleassessment_id) REFERENCES public.alleleassessment(id);


--
-- Name: interpretationlog fk_interpretationlog_alleleinterpretation_id_alleleinterpretati; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interpretationlog
    ADD CONSTRAINT fk_interpretationlog_alleleinterpretation_id_alleleinterpretati FOREIGN KEY (alleleinterpretation_id) REFERENCES public.alleleinterpretation(id) ON DELETE CASCADE;


--
-- Name: interpretationlog fk_interpretationlog_allelereport_id_allelereport; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interpretationlog
    ADD CONSTRAINT fk_interpretationlog_allelereport_id_allelereport FOREIGN KEY (allelereport_id) REFERENCES public.allelereport(id);


--
-- Name: interpretationlog fk_interpretationlog_analysisinterpretation_id_analysisinterpre; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interpretationlog
    ADD CONSTRAINT fk_interpretationlog_analysisinterpretation_id_analysisinterpre FOREIGN KEY (analysisinterpretation_id) REFERENCES public.analysisinterpretation(id) ON DELETE CASCADE;


--
-- Name: interpretationlog fk_interpretationlog_user_id_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interpretationlog
    ADD CONSTRAINT fk_interpretationlog_user_id_user FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: interpretationstatehistory fk_interpretationstatehistory_alleleinterpretation_id_alleleint; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interpretationstatehistory
    ADD CONSTRAINT fk_interpretationstatehistory_alleleinterpretation_id_alleleint FOREIGN KEY (alleleinterpretation_id) REFERENCES public.alleleinterpretation(id) ON DELETE CASCADE;


--
-- Name: interpretationstatehistory fk_interpretationstatehistory_analysisinterpretation_id_analysi; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interpretationstatehistory
    ADD CONSTRAINT fk_interpretationstatehistory_analysisinterpretation_id_analysi FOREIGN KEY (analysisinterpretation_id) REFERENCES public.analysisinterpretation(id) ON DELETE CASCADE;


--
-- Name: interpretationstatehistory fk_interpretationstatehistory_user_id_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interpretationstatehistory
    ADD CONSTRAINT fk_interpretationstatehistory_user_id_user FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: phenotype fk_phenotype_gene_id_gene; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype
    ADD CONSTRAINT fk_phenotype_gene_id_gene FOREIGN KEY (gene_id) REFERENCES public.gene(hgnc_id);


--
-- Name: reference fk_reference_attachment_id_attachment; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reference
    ADD CONSTRAINT fk_reference_attachment_id_attachment FOREIGN KEY (attachment_id) REFERENCES public.attachment(id);


--
-- Name: referenceassessment fk_referenceassessment_allele_id_allele; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referenceassessment
    ADD CONSTRAINT fk_referenceassessment_allele_id_allele FOREIGN KEY (allele_id) REFERENCES public.allele(id);


--
-- Name: referenceassessment fk_referenceassessment_analysis_id_analysis; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referenceassessment
    ADD CONSTRAINT fk_referenceassessment_analysis_id_analysis FOREIGN KEY (analysis_id) REFERENCES public.analysis(id) ON DELETE SET NULL;


--
-- Name: referenceassessment fk_referenceassessment_genepanel_name_genepanel; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referenceassessment
    ADD CONSTRAINT fk_referenceassessment_genepanel_name_genepanel FOREIGN KEY (genepanel_name, genepanel_version) REFERENCES public.genepanel(name, version);


--
-- Name: referenceassessment fk_referenceassessment_previous_assessment_id_referenceassessme; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referenceassessment
    ADD CONSTRAINT fk_referenceassessment_previous_assessment_id_referenceassessme FOREIGN KEY (previous_assessment_id) REFERENCES public.referenceassessment(id);


--
-- Name: referenceassessment fk_referenceassessment_reference_id_reference; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referenceassessment
    ADD CONSTRAINT fk_referenceassessment_reference_id_reference FOREIGN KEY (reference_id) REFERENCES public.reference(id);


--
-- Name: referenceassessment fk_referenceassessment_user_id_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referenceassessment
    ADD CONSTRAINT fk_referenceassessment_user_id_user FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: referenceassessment fk_referenceassessment_usergroup_id_usergroup; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referenceassessment
    ADD CONSTRAINT fk_referenceassessment_usergroup_id_usergroup FOREIGN KEY (usergroup_id) REFERENCES public.usergroup(id);


--
-- Name: resourcelog fk_resourcelog_usersession_id_usersession; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resourcelog
    ADD CONSTRAINT fk_resourcelog_usersession_id_usersession FOREIGN KEY (usersession_id) REFERENCES public.usersession(id);


--
-- Name: sample fk_sample_analysis_id_analysis; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sample
    ADD CONSTRAINT fk_sample_analysis_id_analysis FOREIGN KEY (analysis_id) REFERENCES public.analysis(id) ON DELETE CASCADE;


--
-- Name: sample fk_sample_father_id_sample; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sample
    ADD CONSTRAINT fk_sample_father_id_sample FOREIGN KEY (father_id) REFERENCES public.sample(id);


--
-- Name: sample fk_sample_mother_id_sample; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sample
    ADD CONSTRAINT fk_sample_mother_id_sample FOREIGN KEY (mother_id) REFERENCES public.sample(id);


--
-- Name: sample fk_sample_sibling_id_sample; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sample
    ADD CONSTRAINT fk_sample_sibling_id_sample FOREIGN KEY (sibling_id) REFERENCES public.sample(id);


--
-- Name: transcript fk_transcript_gene_id_gene; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transcript
    ADD CONSTRAINT fk_transcript_gene_id_gene FOREIGN KEY (gene_id) REFERENCES public.gene(hgnc_id);


--
-- Name: user fk_user_group_id_usergroup; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT fk_user_group_id_usergroup FOREIGN KEY (group_id) REFERENCES public.usergroup(id);


--
-- Name: usergroup fk_usergroup_default_import_genepanel_name_genepanel; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usergroup
    ADD CONSTRAINT fk_usergroup_default_import_genepanel_name_genepanel FOREIGN KEY (default_import_genepanel_name, default_import_genepanel_version) REFERENCES public.genepanel(name, version);


--
-- Name: usergroupfilterconfig fk_usergroupfilterconfig_filterconfig_id_filterconfig; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usergroupfilterconfig
    ADD CONSTRAINT fk_usergroupfilterconfig_filterconfig_id_filterconfig FOREIGN KEY (filterconfig_id) REFERENCES public.filterconfig(id);


--
-- Name: usergroupfilterconfig fk_usergroupfilterconfig_usergroup_id_usergroup; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usergroupfilterconfig
    ADD CONSTRAINT fk_usergroupfilterconfig_usergroup_id_usergroup FOREIGN KEY (usergroup_id) REFERENCES public.usergroup(id);


--
-- Name: usergroupgenepanel fk_usergroupgenepanel_genepanel_name_genepanel; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usergroupgenepanel
    ADD CONSTRAINT fk_usergroupgenepanel_genepanel_name_genepanel FOREIGN KEY (genepanel_name, genepanel_version) REFERENCES public.genepanel(name, version);


--
-- Name: usergroupgenepanel fk_usergroupgenepanel_usergroup_id_usergroup; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usergroupgenepanel
    ADD CONSTRAINT fk_usergroupgenepanel_usergroup_id_usergroup FOREIGN KEY (usergroup_id) REFERENCES public.usergroup(id);


--
-- Name: useroldpassword fk_useroldpassword_user_id_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.useroldpassword
    ADD CONSTRAINT fk_useroldpassword_user_id_user FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: usersession fk_usersession_user_id_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usersession
    ADD CONSTRAINT fk_usersession_user_id_user FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- PostgreSQL database dump complete
--



