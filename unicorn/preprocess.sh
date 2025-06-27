for f in $(find ../../results/reduced -name "*.json"); do
    dst_tmp_path=${f//reduced/sketches}
    dst_path=${dst_tmp_path//.json/.txt}
    if [ -e $dst_path ]; then continue; fi

    echo "===================="
    echo "Processing $f"
    echo "===================="

    # Parse the JSON provenance to base and stream files (./tmp/)
    python3 parse.py $f

    # Generate sketches from these files
    ./bin/unicorn/main filetype edgelist base ./tmp/normal.txt stream ./tmp/stream.txt sketch ./tmp/sketch.txt decay 100 lambda 0.02 batch 100 chunkify 1 chunk_size 50

    # Cleanup
    mkdir -p $(dirname "${dst_path}")
    mv ./tmp/sketch.txt $dst_path

    rm -r ./tmp
done
